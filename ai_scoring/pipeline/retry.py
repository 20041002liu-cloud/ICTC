import time
from typing import Callable, TypeVar

T = TypeVar("T")


def run_with_retry(func: Callable[[], T], attempts: int, backoff_seconds: float) -> T:
    last_exc = None
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except Exception as exc:
            last_exc = exc
            if attempt < attempts:
                time.sleep(backoff_seconds * attempt)

    if last_exc:
        raise last_exc
    raise RuntimeError("Retry failed without exception.")
