import time

from queuectl_pkg.migrations import init_db
from queuectl_pkg.models import Job
from queuectl_pkg.storage import add_job, get_job
from queuectl_pkg.utils import backoff_delay





def test_backoff_delay():
    assert backoff_delay(2, 0) >= 1
    assert backoff_delay(2, 1) == 2
    assert backoff_delay(2, 3) == 8


def test_add_and_get_job(tmp_path):
    dbfile = tmp_path / "test.db"
    # ensure db module uses this file
    from queuectl_pkg import db as _db
    _db.DB_PATH = dbfile
    init_db(path=str(dbfile))
    j = Job(id="t1", command="echo hi", max_retries=1)
    add_job(j)
    got = get_job("t1")
    assert got["id"] == "t1"
    assert got["state"] == "pending"


def test_worker_inprocess_retry_and_dlq(tmp_path):
    dbfile = tmp_path / "test.db"
    from queuectl_pkg import db as _db
    _db.DB_PATH = dbfile
    init_db(path=str(dbfile))
    # failing job
    j = Job(id="wj1", command='python -c "import sys; sys.exit(1)"', max_retries=2)
    add_job(j)

    from queuectl_pkg.worker import _claim_and_run_one_job
    # first attempt
    acted = _claim_and_run_one_job("test-worker")
    assert acted
    mid = get_job("wj1")
    assert mid["attempts"] == 1
    assert mid["state"] in ("failed", "pending") or mid["next_run_at"] >= int(time.time())

    # simulate waiting for backoff (use same backoff calculation)
    from queuectl_pkg.utils import backoff_delay
    delay = backoff_delay(float(2), mid["attempts"]) if mid else 1
    time.sleep(delay + 0.2)
    # second attempt
    acted2 = _claim_and_run_one_job("test-worker")
    assert acted2
    final = get_job("wj1")
    assert final["state"] in ("dead", "failed")
    # after max_retries=2 should be dead
    assert final["attempts"] >= 2
