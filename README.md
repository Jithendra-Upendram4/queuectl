# queuectl

![CI](https://github.com/Jithendra-Upendram4/queuectl/actions/workflows/ci.yml/badge.svg)

Lightweight job queue CLI with SQLite persistence, workers, exponential backoff, DLQ, and graceful shutdown.

Quick start (Windows PowerShell)

1. Create & activate venv

```powershell
cd d:\\backend_flam\\queuectl
python -m venv .venv
.venv\\Scripts\\Activate
```

2. Install deps

```powershell
python -m pip install -r requirements.txt
```

3. Initialize DB

```powershell
python -c "from queuectl_pkg.migrations import init_db; init_db()"
```

4. Enqueue job

Example (PowerShell):

```powershell
# simple echo
python queuectl.py enqueue '{"id":"job1","command":"python -c \"print(\\\'hello\\\')\"","max_retries":3}'

# failing job (useful to test retries/DLQ)
python queuectl.py enqueue '{"id":"job_fail","command":"python -c \"import sys; sys.exit(1)\"","max_retries":2}'
```

5. Start workers (in another shell)

```powershell
python queuectl.py worker start --count 1
```

6. Status & lists

```powershell
python queuectl.py status
python queuectl.py list --state pending
python queuectl.py dlq list
```

Integration test

There's a small integration script that enqueues a failing job and runs the worker claim/run loop in-process (avoids multiprocessing/platform differences):

```powershell
cd d:\\backend_flam\\queuectl
$env:PYTHONPATH='d:\\backend_flam\\queuectl'
python tests\\integration_retry.py
```

Notes

- Persistence: `queuectl.db` (SQLite) in the project root.
- Backoff: controlled via `backoff_base` in config table (defaults to 2).
- DLQ: jobs moved to `dead` when attempts >= `max_retries`.
-- Worker stop: `queuectl worker stop` writes SIGINT to worker PIDs listed in `.queuectl_workers.pid`.
	Worker processes now install signal handlers and will set a shutdown flag and finish the current job before exiting when they receive SIGINT/SIGTERM.

Files

- `queuectl.py` — CLI entrypoint
- `queuectl_pkg/` — package with DB, storage, worker, CLI logic
- `run_tests.sh` — bash test script for Unix-like systems (WSL/macOS/Linux)
- `run_tests.ps1` — PowerShell test script for Windows
- `tests/smoke_test.py` — a small Python smoke test

Demo
----

There is a ready demo you can run that initializes a fresh DB, enqueues a few jobs (success, failing, and a timeout),
starts workers, waits for processing, and writes a human-readable `demo_report.md`.

PowerShell helper (Windows):

```powershell
cd d:\\backend_flam\\queuectl
$env:PYTHONPATH='d:\\backend_flam\\queuectl'
.
\scripts\run_demo.ps1
```

Shell helper (Unix/WSL):

```bash
cd /path/to/queuectl
PYTHONPATH="$(pwd)" ./scripts/run_demo.sh
```

After the demo completes, open `demo_report.md` to see a report like:

```
# QueueCTL Demo Report

## Job demo_ok
- state: completed
- attempts: 1
- output:
```
OK

```

## Job demo_fail
- state: dead
- attempts: 2

## Job demo_timeout
- state: dead
- last_error: timeout: Command 'python -c "import time; time.sleep(3); print(\'done\')"' timed out after 1 seconds
```

This demo is implemented by `demo_presentation_clean.py` and the helper scripts.

Next steps (optional)

- Add job timeout & output logging
- Add pytest-based unit tests and CI
- Replace SQLite locking with a central DB (Postgres) for distributed workers
