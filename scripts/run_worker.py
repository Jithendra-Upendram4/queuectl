import os
import time

proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(proj_root)

from queuectl_pkg.worker import start_workers
ps = start_workers(1)
print('started workers', [p.pid for p in ps])
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('worker script received KeyboardInterrupt')
