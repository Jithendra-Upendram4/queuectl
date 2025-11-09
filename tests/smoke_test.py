"""Simple smoke test for queuectl storage and migrations.

Run with:
    python tests/smoke_test.py

This does not start workers; it validates DB init, enqueue, and read operations.
"""
from queuectl_pkg.migrations import init_db
from queuectl_pkg.models import Job
from queuectl_pkg.storage import add_job, list_jobs


def main():
    init_db()
    print("DB initialized for smoke test")

    j1 = Job(id="job_ok", command="python -c \"print(\\\'OK\\\')\"", max_retries=2)
    j2 = Job(id="job_fail", command="python -c \"import sys; sys.exit(1)\"", max_retries=2)

    add_job(j1)
    add_job(j2)

    jobs = list_jobs()
    print("Enqueued jobs:", [j["id"] for j in jobs])


if __name__ == "__main__":
    main()
