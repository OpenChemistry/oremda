from contextlib import ExitStack, contextmanager


@contextmanager
def run_container(client, name, *args, **kwargs):
    container = client.run(name, *args, **kwargs)
    try:
        yield container
    except Exception as e:
        print(f'An exception was caught: {e}')
        print('Logs:', container.logs())
        raise
    finally:
        container.stop()
        container.remove(v=True)


@contextmanager
def run_containers(client, names, args_list, kwargs_list):
    with ExitStack() as stack:
        containers = []
        try:
            for name, args, kwargs in zip(names, args_list, kwargs_list):
                container = stack.enter_context(
                                run_container(client, name, *args, **kwargs))
                containers.append(container)

            yield containers
        except Exception as e:
            print(f'An exception was caught: {e}')
            print('Logs:')
            for container in containers:
                print(f'{container.id}: {container.logs()}')
            raise
