"""Clean demo presentation script

Use this script for a concise demo run and it writes `demo_report.md` next to this file.
"""
import os
import time
from pathlib import Path

from queuectl_pkg.migrations import init_db
from queuectl_pkg.models import Job
from queuectl_pkg.storage import add_job, list_jobs


DB_FILE = Path(__file__).parent / "queuectl.db"
REPORT = Path(__file__).parent / "demo_report.md"


def enqueue_demo_jobs():
    jobs = [
        Job(id="demo_ok", command="python -c \"print('OK')\"", max_retries=2),
        Job(id="demo_fail", command="python -c \"import sys; sys.exit(1)\"", max_retries=2),
        Job(id="demo_timeout", command="python -c \"import time; time.sleep(3); print('done')\"", max_retries=1, timeout=1),
    ]
    for j in jobs:
        try:
            add_job(j)
            print(f"Enqueued: {j.id}")
        except Exception as e:
            print(f"Could not enqueue {j.id}: {e}")


def all_done(job_ids):
    rows = list_jobs()
    states = {r['id']: r['state'] for r in rows}
    return all(states.get(jid) in ('completed', 'dead') for jid in job_ids)


def write_report(path: Path):
    rows = list_jobs()
    with path.open('w', encoding='utf-8') as f:
        f.write('# QueueCTL Demo Report\n\n')
        f.write(f'Generated at: {time.strftime("%Y-%m-%d %H:%M:%S") }\n\n')
        for r in rows:
            f.write(f'## Job {r["id"]}\n')
            f.write(f'- state: {r["state"]}\n')
            f.write(f'- attempts: {r.get("attempts") or 0}\n')
            f.write(f'- max_retries: {r.get("max_retries")}\n')
            f.write(f'- last_error: {r.get("last_error")}\n')
            out = r.get('output') or ''
            f.write('- output:\n')
            f.write('```\n')
            f.write(str(out))
            f.write('\n```\n\n')
    print(f"Report written to: {path}")


def main():
    os.chdir(Path(__file__).parent)
    if DB_FILE.exists():
        DB_FILE.unlink()
    init_db()
    print('DB initialized (fresh)')
    enqueue_demo_jobs()
    jids = ["demo_ok", "demo_fail", "demo_timeout"]

    from queuectl_pkg.worker import start_workers, SHUTDOWN

    workers = start_workers(2)
    print(f"Started {len(workers)} workers: {[p.pid for p in workers]}")

    deadline = time.time() + 30
    while time.time() < deadline:
        if all_done(jids):
            break
        time.sleep(0.5)

    write_report(REPORT)

    SHUTDOWN.set()
    for p in workers:
        p.join(2)
        if p.is_alive():
            p.terminate()
    print('Workers stopped')


if __name__ == '__main__':
    main()
