import logging
import threading
from Redy.Function import identity
from Redy.Types import *

from .Delegate import Delegate

__all__ = ['Accompany', 'ThreadExit']

_cancel_sign = object()


class Accompany(Generic[T, TR, TE]):
    """
    >>> from Redy.Async.Accompany import Accompany, Delegate, ThreadExit
    >>> from Redy.Types import *
    >>> import time
    >>> delta = 0.2


    >>> def descriptor_mapping(x: str) -> Type[str]: return x.__class__
    >>> def act1(task: Accompany, product: Any, ctx: Thunk): print(task.events);time.sleep(delta)

    >>> task: Accompany[None, str, Type[str]] = Accompany(
    >>>     lambda: open('b.txt'),
    >>>     descriptor_mapping=lambda _: descriptor_mapping(_),
    >>>     events={str: Delegate(act1)})

    >>> task.run()
    >>> added = False


    >>> def exit_thread(task, product, ctx): print('exit'); raise ThreadExit


    >>> while task.running:
    >>>    print('running')
    >>>    if not added:
    >>>        task.events[str].insert(
    >>>            lambda _, product, ctx: print(product) or time.sleep(delta),
    >>>            where=0)
    >>>        added = True
    >>>    else:
    >>>        task.events[str].insert(exit_thread, 0)

    >>> task.run()
    >>> task.cancel()
    >>> task.run()
    >>> # task.cancel()
    >>> task.wait()

    >>> print(f"finished?: {task.finished}")


    """

    def __init__(self,
                 target: Union[Func[T, Stream[TR]], Thunk[Stream[TR]]],
                 descriptor_mapping: Func[TR, TE] = None,
                 events: Dict[TE, Delegate] = None) -> None:

        # user-writable
        self.target = target
        self.descriptor_mapping = descriptor_mapping if descriptor_mapping else identity
        self.events = events if events else {}
        self.product = None
        self.lock = threading.Lock()

        # user-readonly
        self._finished = None
        self._running = False
        self._thread: threading.Thread = None

    def run(self, *args):
        """
        You can choose whether to use lock method when running threads.
        """
        self._finished = False
        self._running = True
        stream = self.target(*args)

        # noinspection SpellCheckingInspection
        def subr():
            self._running = True
            try:
                for each in stream:
                    self.product = each
                    desc = self.descriptor_mapping(each)
                    event = self.events.get(desc)
                    if event:
                        event(self, each, globals)
                self._finished = True
            except ThreadExit:
                pass
            finally:
                self._running = False

        self._thread = thread = threading.Thread(target=subr, args=())
        thread.start()
        return self

    @property
    def running(self):
        return self._running

    @property
    def finished(self):
        return self._finished

    def cancel(self):
        with self.lock:
            desc_mapping = self.descriptor_mapping
            self.descriptor_mapping = lambda _: _cancel_sign
            self.events[_cancel_sign] = ThreadExit.exit_thread
            while self._running:
                pass
            self.descriptor_mapping = desc_mapping
            return self

    def wait(self):
        self._thread.join()
        return self


class ThreadExit(Exception):
    @staticmethod
    def exit_thread(task: Accompany, product, ctx_getter: Thunk[Ctx]):
        raise ThreadExit
