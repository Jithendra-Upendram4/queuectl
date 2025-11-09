# QueueCTL Demo Report

Generated at: 2025-11-10 00:20:43

## Job demo_ok
- state: completed
- attempts: 1
- max_retries: 2
- last_error: None
- output:
```
OK

```

## Job demo_fail
- state: dead
- attempts: 2
- max_retries: 2
- last_error: 
- output:
```

```

## Job demo_timeout
- state: dead
- attempts: 1
- max_retries: 1
- last_error: timeout: Command 'python -c "import time; time.sleep(3); print('done')"' timed out after 1 seconds
- output:
```
timeout: Command 'python -c "import time; time.sleep(3); print('done')"' timed out after 1 seconds
```

