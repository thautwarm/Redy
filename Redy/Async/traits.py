import threading
import functools


class Atomic:
    _lock: threading.Lock

    @staticmethod
    def with_lock(method):
        def inner(self: Atomic, *args, **kwargs):
            with self._lock:
                return method(self, *args, **kwargs)

        functools.update_wrapper(inner, method)
        return inner
