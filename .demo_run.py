import sys
sys.path.insert(0, r'd:\backend_flam\queuectl')
from queuectl_pkg.migrations import init_db
from queuectl_pkg.models import Job
from queuectl_pkg.storage import add_job, list_jobs
from queuectl_pkg.worker import _claim_and_run_one_job

init_db()
print('DB initialized')

add_job(Job(id='demo_ok', command='python -c "print(\"DEMO OK\")"', max_retries=2))
add_job(Job(id='demo_fail', command='python -c "import sys; sys.exit(1)"', max_retries=2))

print('Enqueued:', [j['id'] for j in list_jobs()])

# process until no more jobs ready
while True:
    got = _claim_and_run_one_job('demo-worker')
    if not got:
        break
print('Final states:')
for j in list_jobs():
    print(j['id'], j['state'], j['attempts'], j.get('last_error'))
