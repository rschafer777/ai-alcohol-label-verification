from __future__ import annotations

import multiprocessing as mp
import queue
import threading
import time
import uuid
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from labelverify.contracts.models import AnalysisResult, ReferenceRecord, VerificationResult
from labelverify.extraction.rapidocr_adapter import RapidOcrAdapter
from labelverify.orchestration.pipeline import (
    AnalysisJob,
    PipelineFailure,
    PipelineJob,
    execute_analysis,
    execute_pipeline,
)


class WorkerNotReady(RuntimeError):
    pass


class WorkerQueueBusy(RuntimeError):
    pass


class WorkerTimedOut(RuntimeError):
    pass


class WorkerExecutionFailed(RuntimeError):
    def __init__(self, code: str, field_or_panel: str | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.field_or_panel = field_or_panel


@dataclass(frozen=True)
class SupervisorSnapshot:
    ready: bool
    generation: int
    active_jobs: int
    timeouts: int
    restarts: int
    child_pid: int | None


class WorkerSupervisor:
    def __init__(
        self,
        model_root: Path,
        *,
        worker_deadline_seconds: float = 9.0,
        acquisition_seconds: float = 0.2,
        build_id: str = "development",
    ) -> None:
        self._model_root = model_root
        self._worker_deadline_seconds = worker_deadline_seconds
        self._acquisition_seconds = acquisition_seconds
        self._build_id = build_id
        self._context = mp.get_context("spawn")
        self._commands: Any | None = None
        self._results: Any | None = None
        self._process: Any | None = None
        self._job_lock = threading.Lock()
        self._lifecycle_lock = threading.Lock()
        self._replacement_threads: set[threading.Thread] = set()
        self._stopping = False
        self._ready = False
        self._generation = 0
        self._active_jobs = 0
        self._timeouts = 0
        self._restarts = 0

    @property
    def ready(self) -> bool:
        return self._ready and bool(self._process and self._process.is_alive())

    def snapshot(self) -> SupervisorSnapshot:
        process = self._process
        return SupervisorSnapshot(
            ready=self.ready,
            generation=self._generation,
            active_jobs=self._active_jobs,
            timeouts=self._timeouts,
            restarts=self._restarts,
            child_pid=process.pid if process and process.is_alive() else None,
        )

    def start(self, readiness_timeout: float = 15.0) -> bool:
        with self._lifecycle_lock:
            if self._stopping:
                return False
            if self.ready:
                return True
            self._ready = False
            self._commands = self._context.Queue(maxsize=1)
            self._results = self._context.Queue(maxsize=2)
            self._generation += 1
            self._process = self._context.Process(
                target=_worker_main,
                args=(
                    self._commands,
                    self._results,
                    str(self._model_root),
                    self._generation,
                ),
                name=f"labelverify-ocr-{self._generation}",
            )
            self._process.start()
            generation = self._generation
            results = self._results
        deadline = time.monotonic() + readiness_timeout
        message: dict[str, Any] | None = None
        while message is None:
            with self._lifecycle_lock:
                if self._stopping or generation != self._generation:
                    return False
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                with self._lifecycle_lock:
                    if generation == self._generation:
                        self._terminate_locked()
                return False
            try:
                message = results.get(timeout=min(0.05, remaining))
            except queue.Empty:
                continue
        with self._lifecycle_lock:
            if self._stopping or generation != self._generation:
                return False
            self._ready = message.get("kind") == "ready"
            if not self._ready:
                self._terminate_locked()
            return self._ready

    def run(
        self,
        request_id: str,
        reference: ReferenceRecord,
        panel_paths: tuple[Path, ...],
    ) -> VerificationResult:
        if not self._job_lock.acquire(timeout=self._acquisition_seconds):
            raise WorkerQueueBusy
        with self._lifecycle_lock:
            if self._stopping or not self.ready:
                self._job_lock.release()
                raise WorkerNotReady
            assert self._commands is not None
            assert self._results is not None
            commands = self._commands
            results = self._results
            self._active_jobs += 1
        job_id = uuid.uuid4().hex
        try:
            deadline = time.monotonic() + self._worker_deadline_seconds
            self._put_command(
                commands,
                {
                    "kind": "job",
                    "jobId": job_id,
                    "requestId": request_id,
                    "buildId": self._build_id,
                    "reference": reference.model_dump(by_alias=True, mode="json"),
                    "panelPaths": [str(path) for path in panel_paths],
                },
                deadline,
            )
            response = self._wait_for_result(results, deadline)
            if response.get("jobId") != job_id:
                self._ready = False
                self._terminate_worker()
                self._schedule_replacement()
                raise WorkerExecutionFailed("internal_error")
            if response.get("kind") == "error":
                raise WorkerExecutionFailed(
                    str(response.get("code", "internal_error")), response.get("fieldOrPanel")
                )
            if response.get("kind") != "result":
                raise WorkerExecutionFailed("internal_error")
            return VerificationResult.model_validate(response["payload"])
        finally:
            with self._lifecycle_lock:
                self._active_jobs -= 1
            self._job_lock.release()

    def analyze(
        self,
        request_id: str,
        panel_paths: tuple[Path, ...],
    ) -> AnalysisResult:
        if not self._job_lock.acquire(timeout=self._acquisition_seconds):
            raise WorkerQueueBusy
        with self._lifecycle_lock:
            if self._stopping or not self.ready:
                self._job_lock.release()
                raise WorkerNotReady
            assert self._commands is not None
            assert self._results is not None
            commands = self._commands
            results = self._results
            self._active_jobs += 1
        job_id = uuid.uuid4().hex
        try:
            deadline = time.monotonic() + self._worker_deadline_seconds
            self._put_command(
                commands,
                {
                    "kind": "analysis",
                    "jobId": job_id,
                    "requestId": request_id,
                    "buildId": self._build_id,
                    "panelPaths": [str(path) for path in panel_paths],
                },
                deadline,
            )
            response = self._wait_for_result(results, deadline)
            if response.get("jobId") != job_id:
                self._ready = False
                self._terminate_worker()
                self._schedule_replacement()
                raise WorkerExecutionFailed("internal_error")
            if response.get("kind") == "error":
                raise WorkerExecutionFailed(
                    str(response.get("code", "internal_error")), response.get("fieldOrPanel")
                )
            if response.get("kind") != "analysis_result":
                raise WorkerExecutionFailed("internal_error")
            return AnalysisResult.model_validate(response["payload"])
        finally:
            with self._lifecycle_lock:
                self._active_jobs -= 1
            self._job_lock.release()

    def stop(self, join_timeout: float = 2.0) -> None:
        with self._lifecycle_lock:
            self._stopping = True
            self._ready = False
            if self._commands is not None and self._process and self._process.is_alive():
                with suppress(queue.Full):
                    self._commands.put_nowait({"kind": "stop"})
                self._process.join(timeout=join_timeout)
            self._terminate_locked()
            replacement_threads = tuple(self._replacement_threads)
        for thread in replacement_threads:
            if thread is not threading.current_thread():
                thread.join(timeout=join_timeout)
        if not self._job_lock.acquire(timeout=max(0.1, join_timeout)):
            raise RuntimeError("Worker job did not drain during shutdown")
        self._job_lock.release()

    def _put_command(self, commands: Any, command: dict[str, Any], deadline: float) -> None:
        while True:
            with self._lifecycle_lock:
                if self._stopping:
                    raise WorkerNotReady
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self._handle_timeout()
            try:
                commands.put(command, timeout=min(0.05, remaining))
                return
            except queue.Full:
                continue

    def _wait_for_result(self, results: Any, deadline: float) -> dict[str, Any]:
        while True:
            with self._lifecycle_lock:
                if self._stopping:
                    raise WorkerNotReady
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self._handle_timeout()
            try:
                response: dict[str, Any] = results.get(timeout=min(0.05, remaining))
                return response
            except queue.Empty:
                continue

    def _handle_timeout(self) -> None:
        with self._lifecycle_lock:
            if self._stopping:
                raise WorkerNotReady
            self._timeouts += 1
            self._ready = False
        self._terminate_worker()
        self._schedule_replacement()
        raise WorkerTimedOut

    def _schedule_replacement(self) -> None:
        with self._lifecycle_lock:
            if self._stopping:
                return
            thread = threading.Thread(target=self._replace_worker, daemon=True)
            self._replacement_threads.add(thread)
            thread.start()

    def _replace_worker(self) -> None:
        current = threading.current_thread()
        try:
            with self._lifecycle_lock:
                if self._stopping:
                    return
                self._restarts += 1
            self.start()
        finally:
            with self._lifecycle_lock:
                self._replacement_threads.discard(current)

    def _terminate_worker(self) -> None:
        with self._lifecycle_lock:
            self._terminate_locked()

    def _terminate_locked(self) -> None:
        process = self._process
        commands = self._commands
        results = self._results
        if process is not None and process.is_alive():
            process.terminate()
            process.join(timeout=2.0)
            if process.is_alive():
                process.kill()
                process.join(timeout=2.0)
        self._process = None
        self._commands = None
        self._results = None
        self._ready = False
        for work_queue in (commands, results):
            if work_queue is None:
                continue
            with suppress(Exception):
                work_queue.close()
            with suppress(Exception):
                work_queue.join_thread()


def _worker_main(commands: Any, results: Any, model_root: str, generation: int) -> None:
    try:
        adapter = RapidOcrAdapter(Path(model_root))
        adapter.initialize()
        results.put({"kind": "ready", "generation": generation})
    except Exception:
        results.put({"kind": "not_ready", "generation": generation})
        return
    while True:
        command = commands.get()
        if command.get("kind") == "stop":
            return
        job_id = command.get("jobId")
        try:
            if command.get("kind") == "analysis":
                analysis_job = AnalysisJob(
                    request_id=str(command["requestId"]),
                    build_id=str(command["buildId"]),
                    panel_paths=tuple(Path(value) for value in command["panelPaths"]),
                )
                analysis = execute_analysis(analysis_job, adapter)
                results.put(
                    {
                        "kind": "analysis_result",
                        "jobId": job_id,
                        "payload": analysis.model_dump(by_alias=True, mode="json"),
                    }
                )
                continue
            reference = ReferenceRecord.model_validate(command["reference"])
            job = PipelineJob(
                request_id=str(command["requestId"]),
                build_id=str(command["buildId"]),
                reference=reference,
                panel_paths=tuple(Path(value) for value in command["panelPaths"]),
            )
            result = execute_pipeline(job, adapter)
            results.put(
                {
                    "kind": "result",
                    "jobId": job_id,
                    "payload": result.model_dump(by_alias=True, mode="json"),
                }
            )
        except PipelineFailure as exc:
            results.put(
                {
                    "kind": "error",
                    "jobId": job_id,
                    "code": exc.code,
                    "fieldOrPanel": exc.field_or_panel,
                }
            )
        except Exception:
            results.put({"kind": "error", "jobId": job_id, "code": "internal_error"})
