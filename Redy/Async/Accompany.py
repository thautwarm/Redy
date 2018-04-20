import threading
from Redy.Typing import *
from .traits import Atomic
from .Delegate import Delegate

__all__ = ['Accompany', 'ThreadExit']

_cancel_sign = object()


class Accompany(Atomic, Generic[T, TR, TE]):
    """

    >>> from Redy.Async.Accompany import Accompany, Delegate, ThreadExit
    >>> from Redy.Typing import *
    >>> from Redy.Tools import Path
    >>> import time
    >>> delta = 0.2

    # we should use a lazy stream to represent event loop.
    >>> def descriptor_mapping(x: str) -> Type[str]: return x.__class__

    # define an action.
    >>> def act1(task: Accompany, product: Any, ctx: Thunk): print(task._events);time.sleep(delta)

    # create a test file
    >>> test_file = Path("./test_io.txt")
    >>> test_file.open('w').write("at three.\\n lo \\n li \\nta")

    # Create a task on an IO stream.
      Once the IO stream yields out a line, `descriptor_mapping` captures it
      and maps it to some status(for instance, just map it to its type).
      Next, the `events` try to get a specific series of actions(a delegate)
      and apply them in order.

    # 在一个IO stream上创建一个任务，
      每当IO stream产出文件的一行，`descriptor_mapping`捕获到它，并将它映射到一个状态值，(比如
      将它映射到它的类型)。
      接下来，　`events`　尝试从这个状态值去获得一系列特定的行动，并依次应用它们。

    >>> task: Accompany[None, str, Type[str]] = Accompany(
    >>>     lambda: open('./test_io.txt'),
    >>>     descriptor_mapping=lambda _: descriptor_mapping(_),
    >>>     events={str: Delegate(act1)})

    # run the task
    >>> task.run()

    # I'm to show how to add a new action to events after the task has been activated,
    >>> new_action_added = False

    >>> while task.running:
    >>>    print('running')
    >>>    if not new_action_added:
    >>>        task._events[str].insert(
    >>>            lambda _, product, ctx: print(product) or time.sleep(delta),
    >>>            where=0)
    >>>        new_action_added = True
    >>>    time.sleep(0.1)

    # More specifically I'm to add an exiting action to `events` to exit the thread.
      Let us use a flag `has_added_exit_method` to represent if the `exit_thread` action has been added.
    >>> has_added_exit_method = False


    >>> def exit_thread(task, product, ctx):
    >>>     print('exit')
    >>>     raise ThreadExit  # just raise `ThreadExit` and you can exit a thread.

    >>> task.run()
    >>> while task.running:
    >>>    print('running')
    >>>    if not has_added_exit_method:
    >>>         task._events[str].insert(exit_thread, where=0)
    >>>         has_added_exit_method = True
    >>>    time.sleep(0.1)


    # run the task again
    >>> task.run()
    # cancel the task
    >>> task.cancel()
    # set new events
    >>> task._events = {str: Delegate(act1)}
    # run again
    >>> task.run()
    # run synchronously with main thread.
    >>> task.wait()


    >>> test_file.delete()
    >>> print(f"finished?: {task.finished}")


    """

    def __init__(self,
                 target: Union[Func[T, Stream[TR]], Thunk[Stream[TR]]],
                 descriptor_mapping: Func[TR, TE] = None,
                 events: Dict[TE, Delegate] = None) -> None:

        # user-writable
        self.target = target
        self._descriptor_mapping = descriptor_mapping if descriptor_mapping else lambda x: x
        self._events = events if events else {}
        self._product = None
        self._lock = threading.Lock()

        # user-readonly
        self._finished = None
        self._running = False

        self._thread: threading.Thread = None

    def run(self, *args):
        """
        You can choose whether to use lock method when running threads.
        """
        if self.running:
            return self

        self._mut_finished(False)  # in case of recovery from a disaster.
        self._mut_running(True)

        stream = self.target(*args)

        # noinspection SpellCheckingInspection
        def subr():
            self._mut_running(True)
            try:
                for each in stream:
                    self._product = each
                    desc = self.descriptor_mapping(each)
                    event = self.events.get(desc)
                    if event:
                        event(self, each, globals)
                self._mut_finished(True)
            except ThreadExit:
                pass
            finally:
                self._mut_running(False)

        self._thread = thread = threading.Thread(target=subr, args=())
        thread.start()
        return self

    def cancel(self):
        desc_mapping = self.descriptor_mapping
        self.descriptor_mapping = lambda _: _cancel_sign
        self.events[_cancel_sign] = ThreadExit.exit_thread
        while self.running:
            pass
        self.descriptor_mapping = desc_mapping
        return self

    def wait(self):
        self._thread.join()
        return self

    @property  # readonly
    def product(self):
        return self._product

    @property
    @Atomic.with_lock
    def descriptor_mapping(self):
        return self._descriptor_mapping

    @descriptor_mapping.setter
    @Atomic.with_lock
    def descriptor_mapping(self, value: Func[TR, TE]):
        self._descriptor_mapping = value

    @property
    @Atomic.with_lock
    def events(self):
        return self._events

    @events.setter
    @Atomic.with_lock
    def events(self, value: Dict[TE, Delegate]):
        self._events = value

    @property
    @Atomic.with_lock
    def running(self):
        return self._running

    @Atomic.with_lock
    def _mut_running(self, value: bool):
        self._running = value

    @property
    @Atomic.with_lock
    def finished(self):
        return self._finished

    @Atomic.with_lock
    def _mut_finished(self, value: bool):
        self._finished = value


class ThreadExit(Exception):
    @staticmethod
    def exit_thread(task: Accompany, product, ctx_getter: Thunk[Ctx]):
        raise ThreadExit
