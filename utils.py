import time
from functools import wraps

def retry(max_attempts=3, delay=1, exceptions=(Exception,)):
    """
    Retry decorator to re-execute a function on failure.

    Args:
        max_attempts (int): Number of retry attempts before raising the error.
        delay (float): Delay in seconds between retries.
        exceptions (tuple): Exception types to catch and retry on.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        print(f"❌ Failed after {attempt} attempts: {e}")
                        raise
                    print(f"⚠️ Attempt {attempt} failed with error: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator
