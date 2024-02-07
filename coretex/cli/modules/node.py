from typing import Tuple, Optional
from pathlib import Path

import logging
import shutil

from . import docker
from .utils import isGPUAvailable
from .nginx import NGINX_DIR
from .ui import clickPrompt, arrowPrompt, highlightEcho, errorEcho, progressEcho, successEcho, stdEcho
from .node_mode import NodeMode
from ..config import CLIConfig
from ..resources import UPDATE_SCRIPT_NAME
from ...networking import networkManager, NetworkRequestError
from ...statistics import getAvailableRamMemory
from ...configuration import CONFIG_DIR
from ...utils import CommandException
from ...entities.model import Model


DOCKER_CONTAINER_NAME = "coretex_node"
DOCKER_CONTAINER_NETWORK = "coretex_node"
DEFAULT_STORAGE_PATH = str(Path.home() / "./coretex")
DEFAULT_RAM_MEMORY = getAvailableRamMemory()
DEFAULT_SWAP_MEMORY = DEFAULT_RAM_MEMORY * 2
DEFAULT_SHARED_MEMORY = 2


class NodeException(Exception):
    pass


def pull(repository: str, tag: str) -> None:
    try:
        progressEcho("Fetching latest node version...")
        docker.imagePull(f"{repository}:{tag}")
        successEcho("Latest node version successfully fetched.")
    except BaseException as ex:
        logging.getLogger("cli").debug(ex, exc_info = ex)
        raise NodeException("Failed to fetch latest node version.")


def isRunning() -> bool:
    return docker.containerExists(DOCKER_CONTAINER_NAME)


def start(dockerImage: str, config: CLIConfig) -> None:
    try:
        progressEcho("Starting Coretex Node...")
        if config.isHTTPS and config.certPemPath is not None and config.keyPemPath is not None:
            docker.startWithNginx(
                DOCKER_CONTAINER_NAME,
                dockerImage,
                config.nodeImage,
                config.serverUrl,
                config.storagePath,
                config.nodeAccessToken,
                config.nodeRam,
                config.nodeSwap,
                config.nodeShared,
                config.nodeMode,
                config.certPemPath,
                config.keyPemPath
            )
        else:
            docker.createNetwork(DOCKER_CONTAINER_NETWORK)
            docker.start(
                DOCKER_CONTAINER_NAME,
                dockerImage,
                config.nodeImage,
                config.serverUrl,
                config.storagePath,
                config.nodeAccessToken,
                config.nodeRam,
                config.nodeSwap,
                config.nodeShared,
                config.nodeMode
            )
        successEcho("Successfully started Coretex Node.")
    except BaseException as ex:
        logging.getLogger("cli").debug(ex, exc_info = ex)
        raise NodeException("Failed to start Coretex Node.")


def stop(isCompose: Optional[bool] = False) -> None:
    try:
        progressEcho("Stopping Coretex Node...")
        if isCompose:
            docker.stopCompose()
            shutil.rmtree(NGINX_DIR)
        else:
            docker.stop(DOCKER_CONTAINER_NAME, DOCKER_CONTAINER_NETWORK)

        (CONFIG_DIR / UPDATE_SCRIPT_NAME).unlink(missing_ok = True)
        (CONFIG_DIR / docker.COMPOSE_FILE_NAME).unlink(missing_ok = True)
        successEcho("Successfully stopped Coretex Node.")
    except BaseException as ex:
        logging.getLogger("cli").debug(ex, exc_info = ex)
        raise NodeException("Failed to stop Coretex Node.")


def shouldUpdate(repository: str, tag: str) -> bool:
    try:
        imageJson = docker.imageInspect(repository, tag)
    except CommandException:
        # imageInspect() will raise an error if image doesn't exist locally
        return True

    try:
        manifestJson = docker.manifestInspect(repository, tag)
    except CommandException:
        return False

    for digest in imageJson["RepoDigests"]:
        if repository in digest and manifestJson["Descriptor"]["digest"] in digest:
            return False

    return True


def registerNode(name: str) -> str:
    response = networkManager.post("service", {
        "machine_name": name,
    })

    if response.hasFailed():
        raise NetworkRequestError(response, "Failed to configure node. Please try again...")

    accessToken = response.getJson(dict).get("access_token")

    if not isinstance(accessToken, str):
        raise TypeError("Something went wrong. Please try again...")

    return accessToken


def selectModelId(retryCount: int = 0) -> int:
    if retryCount >= 3:
        raise RuntimeError("Failed to fetch Coretex Model. Terminating...")

    modelId = clickPrompt("Specify Coretex Model ID that you want to use:", type = int)

    if not isinstance(modelId, int):
        raise TypeError(f"Invalid modelId type \"{type(modelId)}\". Expected: \"int\"")

    try:
        model = Model.fetchById(modelId)
    except:
        errorEcho(f"Failed to fetch model with id {modelId}.")
        return selectModelId(retryCount + 1)

    model.download()

    return modelId


def selectNodeMode() -> Tuple[int, Optional[int]]:
    availableNodeModes = {
        "Execution": NodeMode.execution,
        "Function exclusive": NodeMode.functionExclusive,
        "Function shared": NodeMode.functionShared
    }
    choices = list(availableNodeModes.keys())

    stdEcho("Please select Coretex Node mode:")
    selectedMode = arrowPrompt(choices)

    if not availableNodeModes[selectedMode] == NodeMode.functionExclusive:
        return availableNodeModes[selectedMode], None

    modelId = selectModelId()
    return availableNodeModes[selectedMode], modelId


def configureNode(config: CLIConfig, verbose: bool) -> None:
    highlightEcho("[Node Configuration]")
    config.nodeName = clickPrompt("Node name", type = str)
    config.nodeAccessToken = registerNode(config.nodeName)

    if isGPUAvailable():
        isGPU = clickPrompt("Do you want to allow the Node to access your GPU? (Y/n)", type = bool, default = True)
        config.nodeImage = "gpu" if isGPU else "cpu"
    else:
        config.nodeImage = "cpu"

    config.storagePath = DEFAULT_STORAGE_PATH
    config.nodeRam = DEFAULT_RAM_MEMORY
    config.nodeSwap = DEFAULT_SWAP_MEMORY
    config.nodeShared = DEFAULT_SHARED_MEMORY
    config.isHTTPS = False
    config.certPemPath = None
    config.keyPemPath = None

    if verbose:
        config.storagePath = clickPrompt("Storage path (press enter to use default)", DEFAULT_STORAGE_PATH, type = str)
        config.nodeRam = clickPrompt("Node RAM memory limit in GB (press enter to use default)", type = int, default = DEFAULT_RAM_MEMORY)
        config.nodeSwap = clickPrompt("Node swap memory limit in GB, make sure it is larger than mem limit (press enter to use default)", type = int, default = DEFAULT_SWAP_MEMORY)
        config.nodeShared = clickPrompt("Node POSIX shared memory limit in GB (press enter to use default)", type = int, default = DEFAULT_SHARED_MEMORY)

        if clickPrompt("Use HTTPS (will prompts for certificates)? (Y/n)", type = bool, default = False):
            config.isHTTPS = True
            config.certPemPath = clickPrompt("Enter SSL cert path", type = str)
            config.keyPemPath = clickPrompt("ENTER SSL key path", type = str)

        nodeMode, modelId = selectNodeMode()
        config.nodeMode = nodeMode
        if modelId is not None:
            config.modelId = modelId
    else:
        stdEcho("To configure node manually run coretex node config with --verbose flag.")

    config.save()


def initializeNodeConfiguration() -> None:
    config = CLIConfig.load()

    if config.isNodeValid():
        return

    errorEcho("Node configuration not found.")
    if isRunning():
        stopNode = clickPrompt(
            "Node is already running. Do you wish to stop the Node? (Y/n)",
            type = bool,
            default = True,
            show_default = False
        )

        if not stopNode:
            errorEcho("If you wish to reconfigure your node, use \"coretex node stop\" command first.")
            return

        stop()

    configureNode(config, verbose = False)
    config.save()
