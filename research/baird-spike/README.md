# BAIRD Research Spike

This folder preserves the disposable architecture-feasibility source used before I2R. It is not product implementation and is not a reusable test oracle.

The slice generates synthetic fixtures, runs a bounded RapidOCR pipeline, validates every field against an independent oracle, compares a Tesseract.js candidate, exposes a full-result local parent-child endpoint, measures browser-visible completion, forces timeout/recovery, tests admission, upload, storage, queue, cancellation, and rate controls, and measures process-spawn cold behavior. Results and limitations are documented in `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md`.

The scripts deliberately use local Windows fonts to recreate the recorded synthetic images. Product fixtures and product fonts must not depend on these files.

## Reproduce the retained Python evidence

Run from this directory with Python 3.12 and `uv`:

```powershell
$env:SPIKE_ITERATIONS = '2'
uv run --python 3.12 --with-requirements requirements-research.lock python spike.py
```

Run the fixed 74-attempt Chrome benchmark plus forced timeout/recovery. The harness starts and stops its own managed local service unless `BAIRD_BASE_URL` is explicitly supplied:

```powershell
uv run --python 3.12 --with-requirements requirements-research.lock python browser_benchmark.py
```

For an explicitly managed service, set the same research-only secret in both terminals and point the harness at that service:

```powershell
$env:BAIRD_BENCHMARK_SECRET = 'choose-a-local-test-secret'
uv run --python 3.12 --with-requirements requirements-research.lock python -m uvicorn server:app --host 127.0.0.1 --port 8765
```

```powershell
$env:BAIRD_BENCHMARK_SECRET = 'choose-a-local-test-secret'
$env:BAIRD_BASE_URL = 'http://127.0.0.1:8765'
uv run --python 3.12 --with-requirements requirements-research.lock python browser_benchmark.py
```

Stop the local service, then run five independent process-spawn trials:

```powershell
uv run --python 3.12 --with-requirements requirements-research.lock python cold_start_benchmark.py
```

Run the full application-stack multipart limit, partial-spool timeout, two-copy storage, admission, and rate-control probes:

```powershell
uv run --python 3.12 --with-requirements requirements-research.lock python security_control_benchmark.py
```

Run the actual worker queue, timeout, repeated-cancellation ownership, abort-storm, shutdown, cleanup, and recovery probes:

```powershell
uv run --python 3.12 --with-requirements requirements-research.lock python runtime_control_benchmark.py
```

Chrome stable must be installed for the browser scripts. `requirements-research.lock` contains exact package versions and hashes. The selected OCR model filenames and hashes are in `docs/baird/evidence/MODEL_BOM.md`.

## Comparable Tesseract.js check

```powershell
npm ci
node tesseract_benchmark.mjs
```

The benchmark secret bypasses start-rate accounting only when the research server and harness receive the same explicit value. It does not bypass the two-request admission gate. A negative control proves that the header alone does not bypass rate limits. No release environment may configure this research-only bypass.

Product code must not import from this folder. This retained slice is architecture evidence only. Its separate manifest is independent of the comparison functions, but it is not the sealed release oracle.
