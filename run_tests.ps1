# PowerShell test script for Windows
# Usage: Open PowerShell, activate venv if used, then: .\run_tests.ps1

# init DB
python -c "from queuectl_pkg.migrations import init_db; init_db(); print('db init done')"

# enqueue a successful job
python queuectl.py enqueue '{"id":"job_ok","command":"python -c \"print(\\\'OK\\\')\"","max_retries":2}'

# enqueue a failing job (exit non-zero)
python queuectl.py enqueue '{"id":"job_fail","command":"python -c \"import sys; sys.exit(1)\"","max_retries":2}'

# start one worker in background (PowerShell job)
Start-Job -ScriptBlock { python -c "from queuectl_pkg.worker import start_workers; ps = start_workers(1); print('workers started', [p.pid for p in ps])" }

Start-Sleep -Seconds 2
# wait some seconds to let worker process
Start-Sleep -Seconds 8

# show status and dlq
python queuectl.py status
python queuectl.py list --state dead
