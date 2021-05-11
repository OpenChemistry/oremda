#!/usr/bin/env python

from contextlib import ExitStack, contextmanager
import time

import docker


@contextmanager
def run_container(name, *args, **kwargs):
    client = docker.from_env()
    container = client.containers.run(name, *args, **kwargs)
    try:
        yield container
    except Exception as e:
        print(f'An exception was caught: {e}')
        print('Logs:', container.logs().decode('utf-8'))
        raise
    finally:
        container.stop()
        container.remove(v=True)


@contextmanager
def run_containers(names, args_list, kwargs_list):
    with ExitStack() as stack:
        containers = []
        try:
            for name, args, kwargs in zip(names, args_list, kwargs_list):
                c = stack.enter_context(run_container(name, *args, **kwargs))
                containers.append(c)

            yield containers
        except Exception as e:
            print(f'An exception was caught: {e}')
            print('Logs:')
            for container in containers:
                print(f'{container.id}: {container.logs().decode("utf-8")}')
            raise


if __name__ == '__main__':
    client = docker.from_env()

    # Docker name prefixes
    prefix = 'basic_example_'

    run_list = [
        f'oremda/{prefix}times_two',
        f'oremda/{prefix}minus_three',
        f'oremda/{prefix}viewer',
    ]

    # Queue names must begin with "/"
    base_queue_name = '/queue'
    queue_names = [f'{base_queue_name}{i}' for i in range(len(run_list))]

    loader_image = f'oremda/{prefix}loader'
    loader_kwargs = {
        # The loader will create all of the queues
        'command': queue_names,
        'ipc_mode': 'shareable',
        'detach': True,
    }

    # Keep the loader running until the end, as it hosts the IPC shared memory
    with run_container(loader_image, **loader_kwargs) as load_container:
        # Wait for the load container to start
        while load_container.status != 'created':
            print(f'{load_container.status=}')
            time.sleep(1)

        default_kwargs = {
            'ipc_mode': f'container:{load_container.id}',
            'detach': True,
        }
        containers = [load_container]
        args_list = []
        kwargs_list = []
        for i, name in enumerate(run_list):
            kwargs = default_kwargs.copy()
            from_queue_name = f'{base_queue_name}{i}'
            if i < len(run_list) - 1:
                to_queue_name = f'{base_queue_name}{i + 1}'
                kwargs['command'] = [from_queue_name, to_queue_name]
            else:
                kwargs['command'] = [from_queue_name]

            args_list.append([])
            kwargs_list.append(kwargs)

        # Run the containers
        with run_containers(run_list, args_list,
                            kwargs_list) as run_containers:
            containers += run_containers
            # The final container tells the load container to finish.
            # Wait for the load container to finish.
            load_container.wait()

            # Print out the logs
            for container in containers:
                output = container.logs()
                if output:
                    print(output.decode('utf-8'))
