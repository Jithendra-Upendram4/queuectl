import os
from queuectl_pkg.migrations import init_db
from queuectl_pkg.models import Job
from queuectl_pkg.storage import add_job

# change to project root
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(proj_root)

init_db()

j1 = Job(id='job_ok', command='python -c "print(\'OK\')"', max_retries=2)
j2 = Job(id='job_fail', command='python -c "import sys; sys.exit(1)"', max_retries=2)
add_job(j1)
add_job(j2)
print('enqueued jobs: job_ok, job_fail')
