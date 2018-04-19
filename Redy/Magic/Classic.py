import functools
import threading


def singleton(cls_def):
    initialized = False
    inst = None
    lock = threading.Lock()

    def manager(*args, **kwargs):
        nonlocal inst, initialized
        with lock:
            if initialized:
                return inst
            inst = cls_def(*args, **kwargs)
            initialized = True
            return inst

    functools.update_wrapper(manager, cls_def)
    return manager
