#!/usr/bin/env python

from pathlib import Path
import time

from oremda.clients import Client
from oremda.clients.utils import run_container, run_containers


SINGULARITY_DIR = Path.cwd() / '.singularity'


if __name__ == '__main__':

    client = Client('docker')

    # Docker name prefixes
    prefix = ''

    operator_list = [
        # 'eels_background_subtract',
        # 'add',
        # 'view',
        'ncem_reader',
        'plot',
        'background_fit',
        'subtract',
    ]
    if client.type == 'docker':
        run_list = [f'oremda/{prefix}{name}' for name in operator_list]
        loader_image = f'oremda/{prefix}eels_background'
    elif client.type == 'singularity':
        suffix = '.simg'
        run_list = [f'{SINGULARITY_DIR}/{prefix}{name}{suffix}'
                    for name in operator_list]
        loader_image = f'{SINGULARITY_DIR}/{prefix}eels_background{suffix}'
    else:
        raise Exception(f'Unknown client type: {client.type}')

    volumes = {
        '/run/oremda': {
            'bind': '/run/oremda',
        },
        '/home/alessandro/oremda_data': {
            'bind': '/data',
        },
    }

    loader_kwargs = {
        'ipc_mode': 'shareable',
        'detach': True,
        'volumes': volumes,
        'working_dir': '/data',
    }

    # Keep the loader running until the end, as it hosts the IPC shared memory
    with run_container(client, loader_image,
                       **loader_kwargs) as loader_container:
        # Wait for the loader container to start
        # It'd be nice if we had a cleaner way to do this for singularity...
        time.sleep(5)

        default_kwargs = {
            'ipc_mode': f'container:{loader_container.id}',
            'detach': True,
            'volumes': volumes,
            'working_dir': '/data',
        }
        containers = [loader_container]
        args_list = []
        kwargs_list = []
        for i, name in enumerate(run_list):
            args_list.append([])
            kwargs_list.append(default_kwargs)

        # Run the containers
        with run_containers(client, run_list, args_list,
                            kwargs_list) as run_containers:
            containers += run_containers

            # Wait for the loader container to finish.
            loader_container.wait()

            # Print out the logs
            for container in containers:
                output = container.logs()
                if output:
                    print(output)
