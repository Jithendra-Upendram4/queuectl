from queuectl_pkg.models import Job
from queuectl_pkg.storage import add_job

j1 = Job(id='job_ok', command="python -c \"print('OK')\"", max_retries=2)
j2 = Job(id='job_fail', command="python -c \"import sys; sys.exit(1)\"", max_retries=2)

for j in (j1, j2):
    try:
        add_job(j)
        print('enqueued', j.id)
    except Exception as e:
        print('could not enqueue', j.id, e)
