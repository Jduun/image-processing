import time
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        res = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration_ms = int((end_time - start_time) * 1000)
        return res, duration_ms

    return wrapper
