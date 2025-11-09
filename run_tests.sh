#!/usr/bin/env bash
set -e
source .venv/bin/activate

# init DB fresh
python - <<'PY'
from queuectl_pkg.migrations import init_db
init_db()
print("db init done")
PY

# enqueue a successful job
python queuectl.py enqueue '{"id":"job_ok","command":"echo OK","max_retries":2}'

# enqueue a failing job
python queuectl.py enqueue '{"id":"job_fail","command":"bash -lc "exit 1"","max_retries":2}'

# start one worker in background
python - <<'PY' &
from queuectl_pkg.worker import start_workers
ps = start_workers(1)
print("workers started", [p.pid for p in ps])
PY

sleep 2
# wait some seconds to let worker process
sleep 8

# show status and dlq
python queuectl.py status
python queuectl.py list --state dead || true
