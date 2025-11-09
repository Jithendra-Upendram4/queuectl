import math

def backoff_delay(base: float, attempts: int) -> int:
    # delay = base ** attempts (in seconds). at least 1
    try:
        delay = int(math.pow(base, attempts))
    except Exception:
        delay = 1
    return max(1, delay)
