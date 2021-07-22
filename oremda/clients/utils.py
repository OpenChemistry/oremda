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


def nested_to_flat(nested, delimiter='.'):
    path = ''
    flat = {}

    def recurse(cur):
        nonlocal path
        parent = path
        for key, value in cur.items():
            path = delimiter.join([parent, key]) if parent else key
            if isinstance(value, dict):
                recurse(value)
            else:
                flat[path] = str(value)

        path = parent

    recurse(nested)
    return flat


def flat_to_nested(flat, delimiter='.'):
    nested = {}
    for full_key, value in flat.items():
        keys = full_key.split(delimiter)
        cur = nested
        for key in keys[:-1]:
            cur = cur.setdefault(key, {})

        cur[keys[-1]] = value

    return nested


def flat_get_item(flat, item, delimiter='.'):
    prefix = f'{item}{delimiter}'
    keys = [x for x in flat.keys() if x.startswith(prefix)]

    return {key[len(prefix):]: flat[key] for key in keys}
