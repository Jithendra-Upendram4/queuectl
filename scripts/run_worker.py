import os
import time

from queuectl_pkg.worker import start_workers

def main():
    # run workers from project root when invoked as a script
    proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # keep working directory changes local to script execution
    os.chdir(proj_root)
    ps = start_workers(1)
    print('started workers', [p.pid for p in ps])
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('worker script received KeyboardInterrupt')

if __name__ == '__main__':
    main()
