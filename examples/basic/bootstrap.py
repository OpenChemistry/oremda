#!/usr/bin/env python

from pathlib import Path
import time

from oremda.clients import Client
from oremda.clients.utils import run_container
from oremda.registry import Registry


SINGULARITY_DIR = Path.cwd() / '.singularity'



def main():
    client = Client('docker')

    if client.type == 'docker':
        plasma_image = f'oremda/plasma'
        runner_image = f'oremda/runner'
    elif client.type == 'singularity':
        suffix = '.simg'
        plasma_image = f'{SINGULARITY_DIR}/plasma{suffix}'
        runner_image = f'{SINGULARITY_DIR}/runner{suffix}'
    else:
        raise Exception(f'Unknown client type: {client.type}')

    plasma_volumes = {
        '/run/oremda': {
            'bind': '/run/oremda',
        },
    }

    plasma_kwargs = {
        'ipc_mode': 'shareable',
        'detach': True,
        'volumes': plasma_volumes,
        'working_dir': '/data'
    }

    # Keep the loader running until the end, as it hosts the IPC shared memory
    with run_container(client, plasma_image,
                       **plasma_kwargs) as plasma_container:
        # Wait for the plasma container to start
        # It'd be nice if we had a cleaner way to do this for singularity...
        time.sleep(5)

        runner_volumes = {
            '/run/oremda': {
                'bind': '/run/oremda',
            },
            '/home/alessandro/oremda_data': {
                'bind': '/data',
            },
            # The runner needs to be able to inspect and run docker containers
            '/var/run/docker.sock': {
                'bind': '/var/run/docker.sock'
            },
        }

        runner_kwargs = {
            'ipc_mode': f'container:{plasma_container.id}',
            'detach': True,
            'volumes': runner_volumes,
            'working_dir': '/data',
        }

        with run_container(client, runner_image,
                           **runner_kwargs) as runner_container:
            # Wait for the runner container to finish.
            runner_container.wait()

            # Print out the logs
            for container in [plasma_container, runner_container]:
                output = container.logs()
                if output:
                    pass
                    print(output)


if __name__ == '__main__':
    main()
