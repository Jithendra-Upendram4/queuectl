from .db import execute, query_one, query_all
from .models import Job
from datetime import datetime
from typing import List, Optional

def add_job(job: Job):
    sql = """
    INSERT INTO jobs (id, command, state, attempts, max_retries, created_at, updated_at, next_run_at, last_error, output, timeout)
    VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """
    execute(sql, job.to_row())

def get_job(job_id: str) -> Optional[dict]:
    return query_one("SELECT * FROM jobs WHERE id=?;", (job_id,))

def list_jobs(state: str | None = None) -> List[dict]:
    if state:
        return query_all("SELECT * FROM jobs WHERE state=? ORDER BY created_at;", (state,))
    return query_all("SELECT * FROM jobs ORDER BY created_at;")

def update_job_state(job_id: str, state: str, attempts: int=None, next_run_at: int=None, last_error: str=None, output: str=None, timeout: int=None):
    set_parts = ["state=?, updated_at=?"]
    params = []
    updated_at = datetime.utcnow().isoformat() + "Z"
    params.extend([state, updated_at])
    if attempts is not None:
        set_parts.append("attempts=?")
        params.append(attempts)
    if next_run_at is not None:
        set_parts.append("next_run_at=?")
        params.append(int(next_run_at))
    if last_error is not None:
        set_parts.append("last_error=?")
        params.append(last_error)
    if output is not None:
        set_parts.append("output=?")
        params.append(output)
    if timeout is not None:
        set_parts.append("timeout=?")
        params.append(timeout)
    params.append(job_id)
    sql = f"UPDATE jobs SET {', '.join(set_parts)} WHERE id=?;"
    execute(sql, tuple(params))

def delete_job(job_id: str):
    execute("DELETE FROM jobs WHERE id=?;", (job_id,))
