QueueCTL — one-page summary

What it is

- Lightweight CLI job queue in Python that persists jobs in SQLite and runs jobs using multiple worker processes.
- Features: enqueue jobs, multiple workers, exponential backoff retries, per-job timeout, Dead Letter Queue (DLQ), graceful shutdown, and job output capture.

Quick usage

- Initialize DB:
  python queuectl.py init

- Enqueue a job:
  python queuectl.py enqueue '{"id":"job1","command":"python -c \"print(\'hello\')\""}'

- Start 2 worker processes:
  python queuectl.py worker start --count 2

- Show job details (including stdout/stderr):
  python queuectl.py show job1

- List DLQ and retry a job from the DLQ:
  python queuectl.py dlq list
  python queuectl.py dlq retry job_dead_id

Design & contract (short)

- Inputs: job messages (JSON) with fields: id, command, (optional) max_retries, timeout.
- Outputs: job state transitions persisted in SQLite; job stdout/stderr saved to job record `output` field.
- Error modes: failed jobs are retried with exponential backoff; after exhausting retries, jobs move to `dead` state (DLQ).

Key implementation notes

- Persistence: SQLite single-file `queuectl.db` located in the repo root. Schema managed in `queuectl_pkg/migrations.py`.
- Claiming jobs: workers use a transactional claim (BEGIN IMMEDIATE + conditional UPDATE) to atomically mark a job as processing and avoid duplicate work.
- Backoff: configurable base (default 2) used as delay = base ** attempts (seconds).
- Timeouts: per-job `timeout` enforced via subprocess run; timed-out jobs record a timeout message in `last_error` and the `output` field.
- Graceful shutdown: workers install signal handlers and finish the current job before exiting.

Why this is useful

- Simple, dependency-light queue suitable for demos, interviews, or local automation tasks.
- Clear extension points: swap persistence, add auth, or replace subprocess runner with containerized runtimes.

Next steps you might add

- CI workflow + automated tests on push
- GitHub Actions to run lint & pytest
- A small web dashboard to view and retry DLQ items

Contact

- Replace "Your Name" in LICENSE and commit as author before publishing.
