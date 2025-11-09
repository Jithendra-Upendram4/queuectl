import click
import json
import os
import signal
from .storage import add_job, list_jobs, get_job, update_job_state
from .models import Job
from .migrations import init_db
from .config import get_config, set_config
from .worker import start_workers
from pathlib import Path

PID_FILE = Path(".queuectl_workers.pid")

@click.group()
def main():
    """queuectl CLI - lightweight job queue (use --help for commands)."""
    pass

@main.command()
@click.argument("job_json")
def enqueue(job_json):
    """Enqueue a job: queuectl enqueue '{"id":"job1","command":"echo hi"}'"""
    try:
        data = json.loads(job_json)
    except Exception as e:
        click.echo(f"Invalid JSON: {e}")
        raise SystemExit(1)
    required = {"id","command"}
    if not required.issubset(data.keys()):
        click.echo("Job JSON must contain at least 'id' and 'command'.")
        raise SystemExit(1)
    job = Job(
        id=str(data["id"]),
        command=str(data["command"]),
        max_retries=int(data.get("max_retries", get_config("max_retries") or 3))
    )
    add_job(job)
    click.echo(f"Enqueued job {job.id}")

@main.group()
def worker():
    """Worker management"""
    pass

@worker.command("start")
@click.option("--count", default=1, help="Number of worker processes to start")
def worker_start(count):
    """Start worker processes"""
    # start in background using multiprocessing spawn visible to this process
    procs = start_workers(count)
    # store pids
    with open(PID_FILE, "w") as f:
        f.write(",".join(str(p.pid) for p in procs))
    click.echo(f"Started {len(procs)} workers. PIDs saved to {PID_FILE}")

@worker.command("stop")
def worker_stop():
    """Stop running workers gracefully"""
    if not PID_FILE.exists():
        click.echo("No workers pid file found.")
        return
    pids = PID_FILE.read_text().strip().split(",")
    # send SIGINT to each PID (best-effort). Since we launched processes in same python run, this may be local.
    for pid in pids:
        try:
            os.kill(int(pid), signal.SIGINT)
            click.echo(f"Sent SIGINT to {pid}")
        except Exception as e:
            click.echo(f"Could not signal {pid}: {e}")
    PID_FILE.unlink(missing_ok=True)
    click.echo("Stop requested. Workers will shutdown gracefully after current job.")

@main.command()
def init():
    """Initialize DB"""
    init_db()
    click.echo("DB initialized.")

@main.command()
def status():
    """Show summary of job states & active workers"""
    jobs = list_jobs()
    counts = {}
    for j in jobs:
        counts[j["state"]] = counts.get(j["state"], 0) + 1
    click.echo("Job counts:")
    for st in ("pending","processing","failed","completed","dead"):
        click.echo(f"  {st}: {counts.get(st,0)}")
    # active worker pids
    if PID_FILE.exists():
        click.echo(f"Worker PIDs: {PID_FILE.read_text().strip()}")
    else:
        click.echo("No worker PID file.")

@main.command()
@click.option("--state", default=None, help="Filter jobs by state")
def list(state):
    """List jobs (optionally filter by state)"""
    for j in list_jobs(state):
        click.echo(json.dumps(j))


@main.command()
@click.argument("job_id")
def show(job_id):
    """Show full job details including output: queuectl show <job_id>"""
    j = get_job(job_id)
    if not j:
        click.echo(f"Job {job_id} not found.")
        raise SystemExit(1)
    click.echo(json.dumps(j, indent=2))

@main.group()
def dlq():
    """Dead Letter Queue"""
    pass

@dlq.command("list")
def dlq_list():
    for j in list_jobs("dead"):
        click.echo(json.dumps(j))

@dlq.command("retry")
@click.argument("job_id")
def dlq_retry(job_id):
    j = get_job(job_id)
    if not j:
        click.echo("Job not found.")
        raise SystemExit(1)
    if j["state"] != "dead":
        click.echo("Job is not in dead state.")
        raise SystemExit(1)
    # reset state & attempts & next_run_at
    update_job_state(job_id, "pending", attempts=0, next_run_at=0, last_error=None)
    click.echo(f"Job {job_id} moved back to pending.")

@main.group()
def config():
    """configuration management"""
    pass

@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    set_config(key, value)
    click.echo(f"Config {key} set -> {value}")

@config.command("get")
@click.argument("key")
def config_get(key):
    val = get_config(key)
    click.echo(val or "")

if __name__ == "__main__":
    main()
