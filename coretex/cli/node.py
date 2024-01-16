from typing import Dict

from docker.errors import DockerException, NotFound, APIError
from rich.progress import Progress

import click
import docker

from ..configuration import loadConfig


DOCKER_CONTAINER_NAME = "coretex_node"
DOCKER_CONTAINER_NETWORK = "coretex_node"
TASKS: Dict = {}


# Show task progress (red for download, green for extract)
def showProgress(line: dict, progress: Progress) -> None:
    if line['status'] == 'Downloading':
        id = f'[red][Download {line["id"]}]'
    elif line['status'] == 'Extracting':
        id = f'[green][Extract  {line["id"]}]'
    else:
        # skip other statuses
        return

    if id not in TASKS.keys():
        TASKS[id] = progress.add_task(f"{id}", total=line['progressDetail']['total'])
    else:
        progress.update(TASKS[id], completed=line['progressDetail']['current'])


def imagePull(imageName: str) -> None:
    print(f'Pulling image: {imageName}')
    with Progress() as progress:
        client = docker.from_env()
        resp = client.api.pull(imageName, stream=True, decode=True)
        for line in resp:
            showProgress(line, progress)
        print(type(resp))
        return resp


@click.command()
def start() -> None:
    try:
        client = docker.from_env()
    except DockerException:
        click.echo("Please make sure you have docker installed on your machine and it is up and running.\bMake sure you allow the default socket to be used in Docker Desktop Advanced Settings.")
        return

    config = loadConfig()

    print("Pulling docker image.")
    dockerImage = imagePull("coretexai/coretex-node:latest-cpu")
    # with Progress() as progress:
    #     dockerImage = client.api.pull("coretexai/coretex-node:latest-cpu", stream = True, decode = True)
    #     for line in dockerImage:
    #         show_progress(line, progress)

    dockerContainerConfig = {
        "name": DOCKER_CONTAINER_NAME,
        "environment": {
            "CTX_API_URL": config["serverUrl"],
            "CTX_STORAGE_PATH": config["storagePath"],
            "CTX_NODE_ACCESS_TOKEN": config["nodeAccessToken"]
        },
        "restart_policy": {
            "Name": "always"
        },
        "ports": {
            "21000": "21000"
        },
        "cap_add": [
            "SYS_PTRACE"
        ],
        "network": DOCKER_CONTAINER_NETWORK,
        "mem_limit": config["nodeRam"],
        "memswap_limit": config["nodeSwap"],
        "shm_size": config["nodeSharedMemory"]
    }

    if config["image"] == "gpu":
        dockerContainerConfig["runtime"] = "nvidia"

    try:
        client.networks.create(dockerContainerConfig["network"], driver = "bridge")
        click.echo(f"Successfully created {dockerContainerConfig['network']} network for container.")
    except APIError as e:
        click.echo(f"Error while creating {dockerContainerConfig['network']} network for container.")
        return

    container = client.containers.run(detach = True, image = dockerImage,  **dockerContainerConfig)
    if container is not None:
        click.echo(f"Node with name {container.name} started successfully.")
    else:
        click.echo("Failed to start container.")


@click.command()
def stop() -> None:
    client = docker.from_env()
    try:
        network = client.networks.get(DOCKER_CONTAINER_NETWORK)
        container = client.containers.get(DOCKER_CONTAINER_NAME)

        network.disconnect(container)
        container.stop()

        network.remove()
        container.remove()

        click.echo(f"Container {DOCKER_CONTAINER_NAME} stopped successfully.")
    except NotFound:
        click.echo(f"Container {DOCKER_CONTAINER_NAME} not found.")
    except APIError:
        click.echo(f"Error occurred while stopping container {DOCKER_CONTAINER_NAME}.")


@click.group()
def node() -> None:
    pass


node.add_command(start, "start")
node.add_command(stop, "stop")
