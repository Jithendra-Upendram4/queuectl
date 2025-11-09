"""Demo script: start multiple workers and enqueue several jobs.

Run from project root (PowerShell):

  cd d:\\backend_flam\\queuectl
  $env:PYTHONPATH='d:\\backend_flam\\queuectl'
  python scripts\\multi_worker_demo.py

This script uses a safe `if __name__ == '__main__'` guard to start worker processes
on Windows (multiprocessing spawn) and demonstrates multiple workers processing jobs.
"""
import os
import time
from queuectl_pkg.migrations import init_db
from queuectl_pkg.models import Job
from queuectl_pkg.storage import add_job, list_jobs


def enqueue_jobs(count=6):
    for i in range(count):
        jid = f"mw_job_{i+1}"
        # short sleep command to allow overlap
        # Use single-quoted Python literal and escape inner single quotes so final
        # command is: python -c "import time; time.sleep(1); print('job ... done')"
        cmd = ('python -c "import time; time.sleep(1); print(\'job %s done\')"' % jid)
        try:
            add_job(Job(id=jid, command=cmd, max_retries=1))
        except Exception:
            pass


def print_jobs():
    for j in list_jobs():
        print(j["id"], j["state"], j.get("attempts"), j.get("output"))


if __name__ == '__main__':
    # change to project root
    proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(proj_root)

    init_db()
    enqueue_jobs(6)

    from queuectl_pkg.worker import start_workers

    procs = start_workers(3)
    print('started worker pids:', [p.pid for p in procs])
    try:
        # wait a bit for processing
        time.sleep(6)
        print('jobs after processing:')
        print_jobs()
    finally:
        # request shutdown
        from queuectl_pkg.worker import SHUTDOWN
        SHUTDOWN.set()
        for p in procs:
            p.join(2)
            if p.is_alive():
                p.terminate()
        print('workers stopped')
