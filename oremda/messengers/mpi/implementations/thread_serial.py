from collections import deque
import threading
import time

from mpi4py import MPI

from oremda.utils.concurrency import ThreadPoolSingleton
from oremda.utils.singleton import Singleton

comm = MPI.COMM_WORLD

# The amount of time the loop sleeps each iteration, in seconds
LOOP_INTERVAL = 0.5

# The buffer size of RECV. This is unfortunately required for this messenger.
RECV_BUFFER_SIZE = 1 << 20


class MPIThreadSerialImplementation(Singleton):
    """This class is designed to issue all MPI communications in one thread

    This is designed to be used on a system with a level of thread support
    of MPI_THREAD_SERIALIZED.

    The underlying implementation performs the actual MPI calls on a single
    thread that is in an infinite loop. The send() and recv() functions
    internally wait for this thread to complete before returning.
    """

    def __init__(self):
        self._send_queue = deque()
        self._recv_queue = deque()
        self._futures = []
        self._futures_lock = threading.Lock()

        # Since __init__ should only be called, once, and it should only
        # be called if this is the implementation we are going to use,
        # go ahead and start the loop.
        self._loop_future = ThreadPoolSingleton().submit(self._loop_forever)

    def send(self, msg: dict, dest: int):
        future = MPIFuture()
        self._send_queue.append((future, msg, dest))
        future.result()

    def recv(self, source: int) -> dict:
        future = MPIFuture()
        self._recv_queue.append((future, source))
        return future.result()  # type: ignore

    def _loop_forever(self):
        while threading.main_thread().is_alive():
            try:
                time.sleep(LOOP_INTERVAL)
                self._send_messages()
                self._recv_messages()
                self._test_futures()
            except Exception as e:
                print("_loop_forever caught an exception:", e)
                raise

    def _send_messages(self):
        while self._send_queue:
            try:
                future, msg, dest = self._send_queue.popleft()
            except IndexError:
                # The list was emptied by another thread...
                return

            future.request = comm.isend(msg, dest=dest)

            with self._futures_lock:
                self._futures.append(future)

    def _recv_messages(self):
        while self._recv_queue:
            try:
                future, source = self._recv_queue.popleft()
            except IndexError:
                # The list was emptied by another thread...
                return

            buf = bytearray(RECV_BUFFER_SIZE)
            future.request = comm.irecv(buf, source=source)

            with self._futures_lock:
                self._futures.append(future)

    def _test_futures(self):
        with self._futures_lock:
            # These will notify if they are finished...
            self._futures = [x for x in self._futures if not x.test()]


class MPIFuture:
    def __init__(self, request=None):
        self.lock = threading.RLock()
        self.cv = threading.Condition(self.lock)
        self.request = request
        self._result = None
        self._complete = False

    def result(self):
        with self.lock:
            # Wait until we are signaled that it is complete...
            self.cv.wait_for(self.is_complete)
            return self._result

    def is_complete(self):
        with self.lock:
            return self._complete

    def test(self):
        with self.lock:
            if self._complete:
                return True

            if self.request is None:
                return False

            # Must test multiple times using a timeout, or else
            # we will sometimes miss receives.
            # FIXME: why???
            complete = False
            result = None
            timeout = 0.001
            start = time.time()
            while time.time() < start + timeout and not complete:
                complete, result = self.request.test()

            if not complete:
                return False

            self._result = result
            self._complete = complete
            self.cv.notify_all()

        return True

    @property
    def request(self):
        with self.lock:
            return self._request

    @request.setter
    def request(self, v):
        with self.lock:
            self._request = v
