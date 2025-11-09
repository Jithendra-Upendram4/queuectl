"""Integration test: enqueue a failing job and run the worker loop in-process

Run from project root (PowerShell):

  cd d:\\backend_flam\\queuectl
  $env:PYTHONPATH='d:\\backend_flam\\queuectl'; python tests\\integration_retry.py

This script uses the internal claim-and-run function to avoid multiprocessing complexities
on Windows and demonstrates retries and DLQ behavior.
"""

import os
import time
import json

from queuectl_pkg.migrations import init_db
from queuectl_pkg.models import Job
from queuectl_pkg.storage import add_job, get_job


def _ensure_cwd():
    # When running as a script, set cwd to project root so relative DB path works.
    proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    try:
        os.chdir(proj_root)
    except Exception:
        # best-effort; CI/test runners usually already run from project root
        pass


_ensure_cwd()

init_db()

job_id = "integration_fail"
try:
    # create a failing job
    j = Job(id=job_id, command='python -c "import sys; sys.exit(1)"', max_retries=2)
    add_job(j)
except Exception:
    # may already exist from a prior run
    pass

from queuectl_pkg.worker import _claim_and_run_one_job

print("Starting in-process worker loop to process job and exercise retries...")
start = time.time()
deadline = start + 60
while time.time() < deadline:
    acted = _claim_and_run_one_job("integration-worker")
    if not acted:
        # nothing to do right now
        time.sleep(0.5)
        continue
    job = get_job(job_id)
    print("job status:", json.dumps(job, indent=2))
    if job and job["state"] in ("dead", "completed"):
        break
    # loop again to pick up retry when next_run_at is reached
    time.sleep(0.2)

final = get_job(job_id)
print("Final job state:", json.dumps(final, indent=2))
