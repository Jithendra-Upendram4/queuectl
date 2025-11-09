import sys
sys.path.insert(0, r'd:\backend_flam\queuectl')
from queuectl_pkg.migrations import init_db
from queuectl_pkg.storage import add_job, list_jobs
from queuectl_pkg.models import Job
from queuectl_pkg.worker import _claim_and_run_one_job

init_db()
print('DB init done')

# enqueue jobs
add_job(Job(id='run_ok', command="python -c \"print('OK')\"", max_retries=2))
add_job(Job(id='run_fail', command="python -c \"import sys; sys.exit(1)\"", max_retries=2))

print('Enqueued:', [ (j['id'], j['state']) for j in list_jobs() ])

# process two jobs by calling claim function directly
print('\n-- Claim and run 1')
_claim_and_run_one_job('demo-1')
print('\n-- Claim and run 2')
_claim_and_run_one_job('demo-2')

print('\nFinal jobs:')
for j in list_jobs():
    print(j['id'], j['state'], j['attempts'], j.get('last_error'))

print('\nDead jobs:')
for j in list_jobs('dead'):
    print(j['id'], j['last_error'])
