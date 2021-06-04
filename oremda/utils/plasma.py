from contextlib import contextmanager
import subprocess
import time


@contextmanager
def start_plasma_store(memory, socket_path):
    plasma_store_executable = 'plasma_store'
    command = [plasma_store_executable, '-s', socket_path, '-m', str(memory)]

    stdout_file = None
    stderr_file = None
    try:
        proc = subprocess.Popen(command, stdout=stdout_file,
                                stderr=stderr_file)
        # Wait a second to let it finish starting...
        time.sleep(1)
        rc = proc.poll()
        if rc is not None:
            msg = f'plasma_store exited unexpectedly with code {rc}'
            raise RuntimeError(msg)

        yield proc
    finally:
        if proc.poll() is None:
            proc.kill()
