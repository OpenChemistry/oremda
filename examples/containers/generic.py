import time

from oremda.clients import Client
from oremda.clients.utils import run_container

client = Client('singularity')
image = 'docker://ubuntu'
command = ['echo', 'hello world']

with run_container(client, image, command) as container:
    # Wait for the command to run
    time.sleep(1)

    print(f'{container.logs()=}')
    print(f'{container.id=}')


command = ['echo', 'hello again']
with run_container(client, image, command) as container:
    # Wait for the command to run
    time.sleep(1)

    print(f'{container.logs()=}')
    print(f'{container.id=}')


client = Client('docker')
image = 'ubuntu'
command = ['echo', 'hello world']

with run_container(client, image, command) as container:
    # Wait for the command to run
    time.sleep(1)

    print(f'{container.logs()=}')
    print(f'{container.id=}')


command = ['echo', 'hello again']
with run_container(client, image, command) as container:
    # Wait for the command to run
    time.sleep(1)

    print(f'{container.logs()=}')
    print(f'{container.id=}')
