from __future__ import annotations

import asyncio
import hashlib
import json
import multiprocessing as mp
import os
import shutil
import stat
import tempfile
import threading
import time
import warnings
from collections import OrderedDict, deque
from contextlib import asynccontextmanager
from pathlib import Path

import psutil
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from PIL import Image
from rapidocr import RapidOCR
from starlette.datastructures import FormData, Headers, UploadFile
from starlette.formparsers import MultiPartException, MultiPartParser

import spike


RAW_REQUEST_LIMIT = 25_296_896
FILE_PAYLOAD_LIMIT = 24 * 1024 * 1024
PER_FILE_LIMIT = 8 * 1024 * 1024
REFERENCE_LIMIT = 32 * 1024
MAX_FILES = 6
MAX_IMAGE_PIXELS = 12_000_000
MAX_REQUEST_PIXELS = 36_000_000
MAX_ADMITTED_POSTS = 2
UPLOAD_BODY_DEADLINE_SECONDS = 3.0
WORKER_QUEUE_DEADLINE_SECONDS = 0.20
SPOOL_COPY_FACTOR = 2
SPOOL_RESERVATION_PER_REQUEST = RAW_REQUEST_LIMIT * SPOOL_COPY_FACTOR
SPOOL_QUOTA_BYTES = 128 * 1024 * 1024
MAX_GLOBAL_STARTS_PER_MINUTE = 30
MAX_CLIENT_STARTS_PER_TEN_MINUTES = 20
MAX_LIMITER_KEYS = 4096
LIMITER_KEY_TTL_SECONDS = 900.0
WORKER_DEADLINE_SECONDS = 6.25
ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
EXPECTED_MODEL_HASHES = {
    "en_PP-OCRv3_det_infer.onnx": "ea07c15d38ac40cd69da3c493444ec75b44ff23840553ff8ba102c1219ed39c2",
    "en_PP-OCRv4_rec_infer.onnx": "e8770c967605983d1570cdf5352041dfb68fa0c21664f49f47b155abd3e0e318",
    "ch_ppocr_mobile_v2.0_cls_infer.onnx": "e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c",
}
EXPECTED_REGISTRY_HASH = "f1b357c1ebcc261d6b37cf187e44e8501acda31f397d9414101b0cbb8e89adf1"
EXPECTED_RULES_HASH = "8c7051123f958997781999042efd2d3090f17fa60f39bdf54fee58d811c11c45"
EXPECTED_CHECK_REGISTRY_VERSION = "baird-spike-v3"
EXPECTED_RULES_REGISTRY_VERSION = "1.0.0"
SPOOL_ROOT = Path(os.environ.get("LABELVERIFY_SPOOL_ROOT", Path(tempfile.gettempdir()) / "labelverify-spool"))
SPOOL_ROOT.mkdir(parents=True, exist_ok=True)
tempfile.tempdir = str(SPOOL_ROOT)


class UploadBodyDeadlineExceeded(TimeoutError):
    pass


class RawRequestLimitExceeded(ValueError):
    pass


class UploadMultipartLimitExceeded(MultiPartException):
    pass


class WorkerQueueBusy(RuntimeError):
    pass


class BoundedMultiPartParser(MultiPartParser):
    """Own the exact parser limits and close partial files on every exception."""

    def __init__(self, headers, stream):
        super().__init__(
            headers,
            stream,
            max_files=MAX_FILES,
            max_fields=1,
            max_part_size=REFERENCE_LIMIT,
        )
        self._current_file_bytes = 0
        self._aggregate_file_bytes = 0

    def on_part_begin(self):
        super().on_part_begin()
        self._current_file_bytes = 0

    def on_headers_finished(self):
        try:
            super().on_headers_finished()
        except MultiPartException as exc:
            raise UploadMultipartLimitExceeded(str(exc)) from exc

    def on_part_data(self, data, start, end):
        size = end - start
        if self._current_part.file is not None:
            self._current_file_bytes += size
            self._aggregate_file_bytes += size
            if self._current_file_bytes > PER_FILE_LIMIT:
                raise UploadMultipartLimitExceeded("File exceeded the 8 MiB encoded limit")
            if self._aggregate_file_bytes > FILE_PAYLOAD_LIMIT:
                raise UploadMultipartLimitExceeded("Files exceeded the 24 MiB aggregate encoded limit")
        try:
            super().on_part_data(data, start, end)
        except MultiPartException as exc:
            raise UploadMultipartLimitExceeded(str(exc)) from exc

    async def parse(self):
        try:
            return await super().parse()
        except BaseException:
            for handle in self._files_to_close_on_error:
                handle.close()
            raise


def close_form_files(form: FormData | None):
    if form is None:
        return
    for _, value in form.multi_items():
        if isinstance(value, UploadFile):
            value.file.close()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_runtime_assets() -> dict:
    model_root = Path(os.environ.get("LABELVERIFY_MODEL_ROOT", Path(__import__("rapidocr").__file__).resolve().parent / "models"))
    expected_registry = os.environ.get("BAIRD_TEST_REGISTRY_HASH_OVERRIDE", EXPECTED_REGISTRY_HASH)
    registry_actual = sha256_file(spike.CHECK_REGISTRY_PATH)
    if registry_actual != expected_registry:
        raise RuntimeError("selected-check registry hash mismatch")
    if spike.CHECK_REGISTRY.get("registry_version") != EXPECTED_CHECK_REGISTRY_VERSION:
        raise RuntimeError("selected-check registry version mismatch")
    expected_models = dict(EXPECTED_MODEL_HASHES)
    model_override = os.environ.get("BAIRD_TEST_MODEL_HASH_OVERRIDE")
    if model_override:
        expected_models["en_PP-OCRv3_det_infer.onnx"] = model_override
    expected_rules = os.environ.get("BAIRD_TEST_RULES_HASH_OVERRIDE", EXPECTED_RULES_HASH)
    rules_actual = sha256_file(spike.REGULATORY_RULES_PATH)
    if rules_actual != expected_rules:
        raise RuntimeError("regulatory rules hash mismatch")
    if spike.REGULATORY_RULES.get("registry_version") != EXPECTED_RULES_REGISTRY_VERSION:
        raise RuntimeError("regulatory rules version mismatch")
    verified_models = {}
    governed_paths = [spike.CHECK_REGISTRY_PATH, spike.REGULATORY_RULES_PATH]
    for name, expected in expected_models.items():
        model_path = model_root / name
        actual = sha256_file(model_path)
        if actual != expected:
            raise RuntimeError(f"model hash mismatch: {name}")
        verified_models[name] = actual
        governed_paths.append(model_path)
    writable = [str(path) for path in governed_paths if path.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)]
    research_override = os.environ.get("BAIRD_RESEARCH_ALLOW_WRITABLE_ASSETS") == "1"
    if writable and not research_override:
        raise RuntimeError("governed runtime assets are writable")
    return {
        "registry_sha256": registry_actual,
        "regulatory_rules_sha256": rules_actual,
        "model_sha256": verified_models,
        "governed_assets_readonly": not writable,
        "research_writable_asset_override": research_override,
    }


def worker_main(connection):
    try:
        proc = psutil.Process()
        affinity = proc.cpu_affinity()
        proc.cpu_affinity(affinity[:2])
        started = time.perf_counter()
        verified_assets = verify_runtime_assets()
        ocr = RapidOCR(params=spike.ocr_params())
        warmup_path = spike.FIXTURES / "S01_clean_one" / "panel-1.jpg"
        warmup_sheet, _, _ = spike.contact_sheet([str(warmup_path)])
        ocr(warmup_sheet, unclip_ratio=2.0, box_thresh=0.35, text_score=0.35)
        connection.send({
            "type": "ready",
            "worker_pid": proc.pid,
            "worker_init_warmup_ms": round((time.perf_counter() - started) * 1000, 2),
            "worker_rss_bytes": proc.memory_info().rss,
            **verified_assets,
        })
    except Exception as exc:
        connection.send({"type": "startup_error", "error_type": type(exc).__name__, "message": str(exc)})
        return
    while True:
        message = connection.recv()
        if message["type"] == "stop":
            return
        if message["type"] != "verify":
            continue
        if message.get("force_hang"):
            time.sleep(WORKER_DEADLINE_SECONDS + 5.0)
        with spike.PeakSampler() as peak:
            try:
                row = spike.run_paths(
                    ocr,
                    message["paths"],
                    message["reference"],
                    "architecture-slice",
                    None,
                    message["iteration"],
                )
                connection.send({"type": "result", "row": row, "worker_peak_rss_bytes": peak.peak})
            except Exception as exc:
                connection.send({"type": "error", "error_type": type(exc).__name__, "message": str(exc)})


class OCRWorker:
    def __init__(self):
        self.context = mp.get_context("spawn")
        self.verify_lock = threading.Lock()
        self.state_lock = threading.RLock()
        self.restart_lock = threading.Lock()
        self.process = None
        self.connection = None
        self.ready_metadata = None
        self.restart_thread = None
        self.accept_restarts = True

    def start(self):
        parent, child = self.context.Pipe()
        process = self.context.Process(target=worker_main, args=(child,), name="labelverify-ocr-worker")
        process.start()
        if not parent.poll(15.0):
            process.terminate()
            process.join(3.0)
            raise RuntimeError("OCR worker readiness deadline exceeded")
        message = parent.recv()
        if message.get("type") != "ready":
            process.join(3.0)
            raise RuntimeError(f"OCR worker failed readiness: {message.get('message', 'unknown startup error')}")
        with self.state_lock:
            self.process, self.connection, self.ready_metadata = process, parent, message

    def is_ready(self):
        with self.state_lock:
            return bool(self.ready_metadata and self.process and self.process.is_alive())

    def stop(self):
        with self.state_lock:
            self._stop_locked()

    def _stop_locked(self):
        if self.connection and self.process and self.process.is_alive():
            try:
                self.connection.send({"type": "stop"})
                self.process.join(2.0)
            except (BrokenPipeError, EOFError):
                pass
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join(3.0)
        self.process, self.connection, self.ready_metadata = None, None, None

    def _kill_locked(self):
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join(0.25)
        if self.process and self.process.is_alive():
            self.process.kill()
            self.process.join(0.25)
        self.process, self.connection, self.ready_metadata = None, None, None

    def _restart(self):
        with self.restart_lock:
            if not self.accept_restarts:
                return
            try:
                self.start()
            except Exception:
                return

    def restart_async(self):
        with self.state_lock:
            if not self.accept_restarts:
                return
            if self.restart_thread and self.restart_thread.is_alive():
                return
            self.restart_thread = threading.Thread(target=self._restart, name="labelverify-worker-restart", daemon=True)
            self.restart_thread.start()

    def verify(self, paths, reference, iteration, force_hang=False):
        if not self.verify_lock.acquire(timeout=WORKER_QUEUE_DEADLINE_SECONDS):
            raise WorkerQueueBusy("OCR worker queue wait exceeded 200 ms")
        try:
            with self.state_lock:
                if not self.is_ready():
                    self.restart_async()
                    raise RuntimeError("OCR worker is warming")
                process, connection = self.process, self.connection
            connection.send({"type": "verify", "paths": paths, "reference": reference, "iteration": iteration, "force_hang": force_hang})
            if not connection.poll(WORKER_DEADLINE_SECONDS):
                with self.state_lock:
                    if self.process is process:
                        self._kill_locked()
                self.restart_async()
                raise TimeoutError("OCR worker hard safety deadline exceeded")
            message = connection.recv()
            if message["type"] == "error":
                raise RuntimeError(f"Worker {message['error_type']}: {message['message']}")
            return message
        finally:
            self.verify_lock.release()


worker = OCRWorker()
owned_worker_jobs = set()
control_probe = {"route_entries": 0, "decoder_entries": 0}


async def run_owned_worker_job(paths, reference, iteration, force_hang, request_dir):
    try:
        return await asyncio.to_thread(worker.verify, paths, reference, iteration, force_hang)
    finally:
        shutil.rmtree(request_dir, ignore_errors=True)


async def await_owned_job(task):
    """Defer any number of caller cancellations until worker ownership ends."""
    cancelled = False
    while True:
        try:
            result = await asyncio.shield(task)
            break
        except asyncio.CancelledError:
            cancelled = True
            current = asyncio.current_task()
            if current is not None:
                current.uncancel()
        except BaseException:
            if cancelled:
                raise asyncio.CancelledError
            raise
    if cancelled:
        raise asyncio.CancelledError
    return result


@asynccontextmanager
async def lifespan(app):
    process_started = time.perf_counter()
    app.state.accepting = False
    spike.make_cases()
    worker.accept_restarts = True
    worker.start()
    app.state.ready = True
    app.state.accepting = True
    print(json.dumps({
        "event": "ready",
        "process_to_ready_ms": round((time.perf_counter() - process_started) * 1000, 2),
        **worker.ready_metadata,
    }), flush=True)
    try:
        yield
    finally:
        app.state.accepting = False
        app.state.ready = False
        worker.accept_restarts = False
        pending = set(owned_worker_jobs)
        if pending:
            _, pending = await asyncio.wait(
                pending,
                timeout=WORKER_DEADLINE_SECONDS + WORKER_QUEUE_DEADLINE_SECONDS + 1.0,
            )
        if pending:
            await asyncio.to_thread(worker.stop)
            await asyncio.gather(*pending, return_exceptions=True)
        await asyncio.to_thread(worker.stop)


class RawBodyLimitMiddleware:
    def __init__(self, app, max_bytes):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("method") != "POST":
            return await self.app(scope, receive, send)
        received = 0
        body_complete = False
        body_deadline = time.monotonic() + UPLOAD_BODY_DEADLINE_SECONDS
        content_lengths = [value for key, value in scope.get("headers", []) if key.lower() == b"content-length"]
        if len(content_lengths) > 1:
            return await JSONResponse({"error": "invalid_content_length"}, status_code=400)(scope, receive, send)
        if content_lengths:
            try:
                declared = int(content_lengths[0])
            except ValueError:
                return await JSONResponse({"error": "invalid_content_length"}, status_code=400)(scope, receive, send)
            if declared < 0:
                return await JSONResponse({"error": "invalid_content_length"}, status_code=400)(scope, receive, send)
            if declared > self.max_bytes:
                return await JSONResponse({"error": "request_too_large"}, status_code=413)(scope, receive, send)

        async def guarded_receive():
            nonlocal received, body_complete
            if body_complete:
                return await receive()
            remaining = body_deadline - time.monotonic()
            if remaining <= 0:
                raise UploadBodyDeadlineExceeded("total upload body deadline exceeded")
            try:
                message = await asyncio.wait_for(receive(), timeout=remaining)
            except asyncio.TimeoutError as exc:
                raise UploadBodyDeadlineExceeded("total upload body deadline exceeded") from exc
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    raise RawRequestLimitExceeded("raw request limit exceeded")
                if not message.get("more_body", False):
                    body_complete = True
            return message

        try:
            return await self.app(scope, guarded_receive, send)
        except RawRequestLimitExceeded as exc:
            response = JSONResponse({"error": "request_too_large", "message": str(exc)}, status_code=413, headers={"Cache-Control": "no-store, private", "Pragma": "no-cache"})
            return await response(scope, receive, send)
        except UploadBodyDeadlineExceeded as exc:
            response = JSONResponse({"error": "upload_timeout", "message": str(exc)}, status_code=408, headers={"Cache-Control": "no-store, private", "Pragma": "no-cache"})
            return await response(scope, receive, send)


class BoundedMultipartMiddleware:
    """Parse the verification form once with the selected application limits."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if (
            scope["type"] != "http"
            or scope.get("method") != "POST"
            or scope.get("path") != "/api/v1/verifications"
        ):
            return await self.app(scope, receive, send)
        form = None
        downstream_started = False
        try:
            request = Request(scope, receive=receive)
            parser = BoundedMultiPartParser(Headers(scope=scope), request.stream())
            form = await parser.parse()
            items = list(form.multi_items())
            if any(name not in {"reference", "files"} for name, _ in items):
                return await JSONResponse({"error": "invalid_form_schema"}, status_code=422)(scope, receive, send)
            references = form.getlist("reference")
            files = form.getlist("files")
            if len(references) != 1 or not isinstance(references[0], str):
                return await JSONResponse({"error": "invalid_reference"}, status_code=422)(scope, receive, send)
            if not 1 <= len(files) <= MAX_FILES or any(not isinstance(item, UploadFile) for item in files):
                return await JSONResponse({"error": "invalid_panel_count", "message": "Supply 1 to 6 label images."}, status_code=422)(scope, receive, send)
            downstream_scope = dict(scope)
            downstream_scope["labelverify.reference"] = references[0]
            downstream_scope["labelverify.files"] = files
            delivered = False

            async def empty_receive():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": b"", "more_body": False}
                return {"type": "http.disconnect"}

            downstream_started = True
            return await self.app(downstream_scope, empty_receive, send)
        except (UploadBodyDeadlineExceeded, RawRequestLimitExceeded):
            raise
        except UploadMultipartLimitExceeded as exc:
            if downstream_started:
                raise
            return await JSONResponse({"error": "multipart_limit_exceeded", "message": str(exc)}, status_code=413)(scope, receive, send)
        except MultiPartException as exc:
            if downstream_started:
                raise
            return await JSONResponse({"error": "invalid_multipart", "message": str(exc)}, status_code=400)(scope, receive, send)
        except Exception:
            if downstream_started:
                raise
            return await JSONResponse({"error": "invalid_multipart"}, status_code=400)(scope, receive, send)
        finally:
            close_form_files(form)


class AdmissionController:
    def __init__(self):
        self.lock = threading.Lock()
        self.secret = os.urandom(32)
        self.inflight = 0
        self.spool_reserved = 0
        self.global_starts = deque()
        self.clients = OrderedDict()

    def _key(self, scope):
        host = str((scope.get("client") or ("unknown", 0))[0])
        return hashlib.blake2s(host.encode("utf-8"), key=self.secret, digest_size=16).hexdigest()

    def acquire(self, scope):
        now = time.monotonic()
        key = self._key(scope)
        headers = {name.lower(): value for name, value in scope.get("headers", [])}
        benchmark_secret = os.environ.get("BAIRD_BENCHMARK_SECRET")
        benchmark_bypass = bool(
            benchmark_secret
            and headers.get(b"x-baird-benchmark") == benchmark_secret.encode("utf-8")
        )
        with self.lock:
            while self.global_starts and self.global_starts[0] <= now - 60.0:
                self.global_starts.popleft()
            for old_key, record in list(self.clients.items()):
                if record["active"] == 0 and record["last_seen"] <= now - LIMITER_KEY_TTL_SECONDS:
                    del self.clients[old_key]
            if self.inflight >= MAX_ADMITTED_POSTS or self.spool_reserved + SPOOL_RESERVATION_PER_REQUEST > SPOOL_QUOTA_BYTES:
                return None, 503, "verification_capacity_busy"
            record = self.clients.get(key)
            if record is None:
                while len(self.clients) >= MAX_LIMITER_KEYS:
                    evictable = next((item for item in self.clients.items() if item[1]["active"] == 0), None)
                    if not evictable:
                        return None, 503, "limiter_capacity_busy"
                    del self.clients[evictable[0]]
                record = {"starts": deque(), "active": 0, "last_seen": now}
                self.clients[key] = record
            while record["starts"] and record["starts"][0] <= now - 600.0:
                record["starts"].popleft()
            if record["active"] >= 1 or (not benchmark_bypass and len(record["starts"]) >= MAX_CLIENT_STARTS_PER_TEN_MINUTES):
                return None, 429, "client_rate_limited"
            if not benchmark_bypass and len(self.global_starts) >= MAX_GLOBAL_STARTS_PER_MINUTE:
                return None, 503, "global_start_rate_limited"
            self.inflight += 1
            self.spool_reserved += SPOOL_RESERVATION_PER_REQUEST
            record["active"] += 1
            record["last_seen"] = now
            if not benchmark_bypass:
                record["starts"].append(now)
                self.global_starts.append(now)
            self.clients.move_to_end(key)
            return key, None, None

    def release(self, key):
        with self.lock:
            self.inflight = max(0, self.inflight - 1)
            self.spool_reserved = max(0, self.spool_reserved - SPOOL_RESERVATION_PER_REQUEST)
            record = self.clients.get(key)
            if record:
                record["active"] = max(0, record["active"] - 1)
                record["last_seen"] = time.monotonic()


admission = AdmissionController()


class AdmissionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("method") != "POST":
            return await self.app(scope, receive, send)
        if not bool(getattr(scope["app"].state, "accepting", False)):
            response = JSONResponse({"error": "service_not_ready"}, status_code=503, headers={"Cache-Control": "no-store, private", "Pragma": "no-cache"})
            return await response(scope, receive, send)
        key, status, code = admission.acquire(scope)
        if status:
            response = JSONResponse({"error": code}, status_code=status, headers={"Cache-Control": "no-store, private", "Pragma": "no-cache"})
            return await response(scope, receive, send)
        try:
            return await self.app(scope, receive, send)
        finally:
            admission.release(key)


class NoStoreMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        async def guarded_send(message):
            if message["type"] == "http.response.start":
                headers = [(name, value) for name, value in message.get("headers", []) if name.lower() not in {b"cache-control", b"pragma"}]
                headers.extend([(b"cache-control", b"no-store, private"), (b"pragma", b"no-cache")])
                message = {**message, "headers": headers}
            await send(message)

        return await self.app(scope, receive, guarded_send)


app = FastAPI(lifespan=lifespan)
app.add_middleware(BoundedMultipartMiddleware)
app.add_middleware(RawBodyLimitMiddleware, max_bytes=RAW_REQUEST_LIMIT)
app.add_middleware(AdmissionMiddleware)
app.add_middleware(NoStoreMiddleware)

PAGE = """<!doctype html><html lang='en'><head><meta charset='utf-8'><title>BAIRD timing slice</title>
<style>table{border-collapse:collapse}th,td{border:1px solid #777;padding:.3rem;text-align:left}.evidence{white-space:nowrap}.evidence button{display:block;margin:.2rem}#evidence-viewer svg{max-width:32rem;border:1px solid #555}#evidence-polygon{fill:none;stroke:#d33;stroke-width:4}</style></head>
<body><main><h1>BAIRD timing slice</h1><input id='files' type='file' multiple accept='image/jpeg,image/png,image/webp'>
<button id='verify'>Verify</button><p id='status' role='status' aria-live='polite'>Ready</p><section id='result' aria-labelledby='result-heading'></section>
<section id='evidence-viewer' aria-labelledby='evidence-heading'><h2 id='evidence-heading'>Label evidence</h2><p id='evidence-status' role='status'>Choose an evidence action.</p><svg id='evidence-svg' hidden><image id='evidence-image'/><polygon id='evidence-polygon'/></svg></section></main>
<script>
const input=document.querySelector('#files'); const button=document.querySelector('#verify');
const cell=(text,cls='')=>{const td=document.createElement('td');td.textContent=text??'Not available';td.className=cls;return td};
let evidenceUrl=null;
const showEvidence=(label,evidence,panelBoxes)=>{if(evidenceUrl)URL.revokeObjectURL(evidenceUrl);const file=input.files[evidence.panel-1];const panel=panelBoxes.find(item=>item[0]===evidence.panel);
 if(!file||!panel){document.querySelector('#evidence-status').textContent='Evidence image is unavailable.';return}const width=panel[3]-panel[1],height=panel[4]-panel[2];evidenceUrl=URL.createObjectURL(file);
 const svg=document.querySelector('#evidence-svg');svg.hidden=false;svg.setAttribute('viewBox',`0 0 ${width} ${height}`);const image=document.querySelector('#evidence-image');image.setAttribute('href',evidenceUrl);image.setAttribute('width',width);image.setAttribute('height',height);
 document.querySelector('#evidence-polygon').setAttribute('points',evidence.polygon.map(point=>`${point[0]-panel[1]},${point[1]-panel[2]}`).join(' '));document.querySelector('#evidence-status').textContent=`Showing ${label} on panel ${evidence.panel}.`;};
button.addEventListener('click', async()=>{const start=performance.now();document.body.dataset.done='false';
 document.querySelector('#status').textContent='Analyzing label';const data=new FormData();
 for(const file of input.files)data.append('files',file);data.append('reference',JSON.stringify(window.reference));
 const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),7500);let response,payload;
 const headers=window.benchmarkSecret?{'X-BAIRD-Benchmark':window.benchmarkSecret}:{};
 try{response=await fetch('/api/v1/verifications',{method:'POST',body:data,headers,signal:controller.signal});payload=await response.json()}catch(error){
  clearTimeout(timer);document.querySelector('#result').replaceChildren();document.querySelector('#status').textContent=error.name==='AbortError'?'Verification timed out. Try a clearer image.':'Verification failed. Try again.';
  document.body.dataset.elapsed=String(performance.now()-start);document.body.dataset.done='true';document.body.dataset.fieldCount='0';return}
 clearTimeout(timer);if(!response.ok){document.querySelector('#result').replaceChildren();document.querySelector('#status').textContent=payload.message||'Verification is temporarily unavailable. Try again.';
  document.body.dataset.elapsed=String(performance.now()-start);document.body.dataset.done='true';document.body.dataset.fieldCount='0';return}const result=payload.result;
 const section=document.querySelector('#result');section.replaceChildren();
 const heading=Object.assign(document.createElement('h2'),{id:'result-heading',textContent:result.summary,tabIndex:-1});section.append(heading);
 const coverage=Object.assign(document.createElement('p'),{id:'coverage',textContent:`${result.panels.count} panel(s) evaluated`});section.append(coverage);
 const table=document.createElement('table');const head=document.createElement('tr');
 for(const label of ['Check','Reference','Observed','State','Reason','Evidence'])head.append(Object.assign(document.createElement('th'),{textContent:label}));
 table.append(head);
 for(const field of result.fields){const row=document.createElement('tr');row.dataset.checkId=field.check_id;
  row.append(cell(field.check_id),cell(field.reference_display),cell(field.extracted_display),cell(field.state,'state'),cell(field.reason_text));
  const evidenceCell=cell(null,'evidence');evidenceCell.replaceChildren();const alternatives=Array.isArray(field.alternatives)?field.alternatives:[];
  const actions=alternatives.length?alternatives.map(item=>({label:item.value,evidence:item.evidence_ref})):field.evidence_ref?[{label:field.check_id,evidence:field.evidence_ref}]:[];
  for(const action of actions){const evidenceButton=document.createElement('button');evidenceButton.type='button';evidenceButton.className='evidence-action';evidenceButton.textContent=`Show ${action.label} on label`;evidenceButton.setAttribute('aria-label',`Show ${action.label} on label`);evidenceButton.dataset.value=action.label;evidenceButton.dataset.panel=String(action.evidence.panel);evidenceButton.dataset.polygon=JSON.stringify(action.evidence.polygon);evidenceButton.addEventListener('click',()=>showEvidence(action.label,action.evidence,payload.panel_boxes));evidenceCell.append(evidenceButton)}
  if(!actions.length)evidenceCell.textContent='Not available';row.append(evidenceCell);table.append(row)}
 section.append(table);const limits=document.createElement('ul');limits.id='limitations';
 for(const text of [...result.human_only_limitations,...result.limitations])limits.append(Object.assign(document.createElement('li'),{textContent:text}));section.append(limits);
 document.querySelector('#status').textContent='Verification complete: '+result.summary;
 requestAnimationFrame(()=>requestAnimationFrame(()=>{document.body.dataset.elapsed=String(performance.now()-start);document.body.dataset.done='true';document.body.dataset.fieldCount=String(result.fields.length);heading.focus();}));
});
</script></body></html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(PAGE, headers={"Cache-Control": "no-store, private", "Pragma": "no-cache"})


@app.get("/health/ready")
async def ready():
    status = bool(getattr(app.state, "ready", False) and worker.is_ready())
    child_count = sum(1 for child in psutil.Process().children(recursive=False) if child.is_running())
    return JSONResponse({"ready": status, "worker": worker.ready_metadata, "ocr_child_count": child_count}, status_code=200 if status else 503, headers={"Cache-Control": "no-store, private", "Pragma": "no-cache"})


@app.post("/api/v1/verifications")
async def verify(request: Request):
    started = time.perf_counter()
    control_probe["route_entries"] += 1
    reference = request.scope["labelverify.reference"]
    files = request.scope["labelverify.files"]
    paths = []
    request_dir = tempfile.mkdtemp(prefix="request-", dir=SPOOL_ROOT)
    worker_owns_dir = False
    try:
        if not worker.is_ready():
            return JSONResponse({"error": "worker_warming", "message": "Verification is warming. Try again shortly."}, status_code=503, headers={"Cache-Control": "no-store, private", "Pragma": "no-cache"})
        parsed_reference = json.loads(reference)
        if not isinstance(parsed_reference, dict):
            return JSONResponse({"error": "invalid_reference"}, status_code=422)
        aggregate_bytes = 0
        aggregate_pixels = 0
        for index, upload in enumerate(files, 1):
            suffix = Path(upload.filename or "panel.jpg").suffix or ".jpg"
            if suffix.lower() not in ALLOWED_SUFFIXES:
                return JSONResponse({"error": "unsupported_image_type"}, status_code=415)
            path = Path(request_dir) / f"panel-{index}{suffix.lower()}"
            file_bytes = 0
            with path.open("wb") as handle:
                while chunk := await upload.read(1024 * 1024):
                    file_bytes += len(chunk)
                    aggregate_bytes += len(chunk)
                    if file_bytes > PER_FILE_LIMIT or aggregate_bytes > FILE_PAYLOAD_LIMIT:
                        return JSONResponse({"error": "file_payload_too_large"}, status_code=413)
                    handle.write(chunk)
            try:
                control_probe["decoder_entries"] += 1
                with warnings.catch_warnings():
                    warnings.simplefilter("error", Image.DecompressionBombWarning)
                    with Image.open(path) as image:
                        if image.format not in ALLOWED_FORMATS:
                            return JSONResponse({"error": "unsupported_image_type"}, status_code=415)
                        pixels = image.width * image.height
                        if pixels > MAX_IMAGE_PIXELS:
                            return JSONResponse({"error": "image_pixel_limit"}, status_code=413)
                        image.verify()
            except (Image.UnidentifiedImageError, OSError, Image.DecompressionBombWarning):
                return JSONResponse({"error": "invalid_image"}, status_code=422)
            aggregate_pixels += pixels
            if aggregate_pixels > MAX_REQUEST_PIXELS:
                return JSONResponse({"error": "request_pixel_limit"}, status_code=413)
            paths.append(str(path))
        force_hang = bool(parsed_reference.pop("_research_force_hang", False))
        worker_task = asyncio.create_task(
            run_owned_worker_job(paths, parsed_reference, 1, force_hang, request_dir)
        )
        worker_owns_dir = True
        owned_worker_jobs.add(worker_task)
        worker_task.add_done_callback(owned_worker_jobs.discard)
        worker_result = await await_owned_job(worker_task)
        row = worker_result["row"]
        result = row["payload"]["result"]
        result["server_duration_ms"] = round((time.perf_counter() - started) * 1000, 2)
        result["server_stage_timings"] = {
            "decode_preprocess_ms": row["decode_preprocess_ms"], "ocr_ms": row["ocr_ms"],
            "rules_serialize_ms": row["rules_serialize_ms"], "worker_pipeline_ms": row["server_pipeline_ms"],
        }
        return JSONResponse({
            "result": result,
            "server_ms": result["server_duration_ms"],
            "decoded_pixels": row["decoded_pixels"],
            "panel_boxes": row["payload"]["panel_boxes"],
            "worker_peak_rss_bytes": worker_result["worker_peak_rss_bytes"],
            "response_bytes": row["response_bytes"],
        }, headers={"Cache-Control": "no-store, private", "Pragma": "no-cache"})
    except (TimeoutError, asyncio.TimeoutError):
        return JSONResponse({"error": "inference_timeout", "message": "The label could not be read within the safety limit"}, status_code=504, headers={"Cache-Control": "no-store, private", "Pragma": "no-cache"})
    except WorkerQueueBusy as exc:
        return JSONResponse({"error": "worker_queue_busy", "message": str(exc)}, status_code=503, headers={"Cache-Control": "no-store, private", "Pragma": "no-cache"})
    except json.JSONDecodeError:
        return JSONResponse({"error": "invalid_reference"}, status_code=422)
    except RuntimeError as exc:
        return JSONResponse({"error": "worker_unavailable", "message": str(exc)}, status_code=503, headers={"Cache-Control": "no-store, private", "Pragma": "no-cache"})
    finally:
        if not worker_owns_dir:
            shutil.rmtree(request_dir, ignore_errors=True)
