import multiprocessing as mp
import time
import subprocess
import os
from .storage import update_job_state
from .config import get_config
from .utils import backoff_delay
from datetime import datetime
from .db import get_conn
import sqlite3

SHUTDOWN = mp.Event()

def _run_command(command: str, timeout: int | None = None) -> tuple[int, str]:
    try:
        completed = subprocess.run(command, shell=True, capture_output=True, timeout=timeout, text=True)
        return completed.returncode, completed.stderr or completed.stdout
    except subprocess.TimeoutExpired as e:
        return 124, f"timeout: {e}"
    except Exception as e:
        return 1, str(e)

def _claim_and_run_one_job(worker_name: str):
    """Atomically claim one pending job whose next_run_at <= now and run it."""
    now_ts = int(time.time())
    conn = get_conn()
    conn.isolation_level = None
    cur = conn.cursor()
    try:
        # Use a transaction to pick a single pending job and set its state to processing
        cur.execute("BEGIN IMMEDIATE;")
        cur.execute(
            "SELECT * FROM jobs WHERE state IN ('pending','failed') AND next_run_at<=? ORDER BY created_at LIMIT 1;",
            (now_ts,)
        )
        row = cur.fetchone()
        if not row:
            conn.commit()
            return False
        job = dict(row)
        job_id = job["id"]
        # double-check locking by updating state to processing
        cur.execute("UPDATE jobs SET state=?, updated_at=? WHERE id=? AND state IN ('pending','failed');",
                    ("processing", datetime.utcnow().isoformat()+"Z", job_id))
        if cur.rowcount == 0:
            conn.commit()
            return False
        conn.commit()
    except sqlite3.OperationalError:
        conn.rollback()
        return False
    finally:
        conn.close()

    # run outside transaction
    print(f"[{worker_name}] Running job {job_id}: {job['command']}")
    # pick up timeout if present
    try:
        job_timeout = job.get("timeout")
        job_timeout = int(job_timeout) if job_timeout else None
    except Exception:
        job_timeout = None
    ret, output = _run_command(job["command"], timeout=job_timeout)
    attempts = job["attempts"] + 1
    max_retries = job["max_retries"]
    base = float(get_config("backoff_base") or 2)
    if ret == 0:
        update_job_state(job_id, "completed", attempts=attempts, next_run_at=0, last_error=None, output=output)
        print(f"[{worker_name}] Job {job_id} completed.")
    else:
        if attempts >= max_retries:
            update_job_state(job_id, "dead", attempts=attempts, next_run_at=0, last_error=str(output), output=str(output))
            print(f"[{worker_name}] Job {job_id} moved to DLQ (dead).")
        else:
            delay = backoff_delay(base, attempts)
            next_ts = int(time.time()) + delay
            update_job_state(job_id, "failed", attempts=attempts, next_run_at=next_ts, last_error=str(output), output=str(output))
            print(f"[{worker_name}] Job {job_id} failed (attempt {attempts}). retry in {delay}s.")

    return True

def worker_loop(worker_id: int, poll_interval: float = 1.0):
    name = f"worker-{worker_id}"
    print(f"[{name}] started (pid={os.getpid()})")
    # install signal handlers to allow graceful shutdown when process receives SIGINT/SIGTERM
    try:
        import signal as _signal

        def _handle(signum, frame):
            print(f"[{name}] signal {signum} received, initiating shutdown")
            SHUTDOWN.set()

        _signal.signal(_signal.SIGINT, _handle)
        _signal.signal(_signal.SIGTERM, _handle)
    except Exception:
        # signals may not be available on some platforms; ignore if installation fails
        pass
    while not SHUTDOWN.is_set():
        got = _claim_and_run_one_job(name)
        if not got:
            time.sleep(poll_interval)
    print(f"[{name}] shutting down (graceful).")

def start_workers(count: int):
    procs = []
    for i in range(count):
        p = mp.Process(target=worker_loop, args=(i+1,), daemon=False)
        p.start()
        procs.append(p)
    return procs

def stop_workers(procs, timeout=10):
    SHUTDOWN.set()
    for p in procs:
        p.join(timeout)
        if p.is_alive():
            p.terminate()
