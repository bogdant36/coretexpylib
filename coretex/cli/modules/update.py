from enum import IntEnum
from pathlib import Path

import requests

from .cron import jobExists, scheduleJob
from .node import DOCKER_CONTAINER_NAME, DOCKER_CONTAINER_NETWORK
from ..config import CLIConfig
from ..resources import RESOURCES_DIR, UPDATE_SCRIPT_NAME
from ...utils import command
from ...configuration import CONFIG_DIR


class NodeStatus(IntEnum):

    inactive     = 1
    active       = 2
    busy         = 3
    deleted      = 4
    reconnecting = 5


def generateUpdateScript(config: CLIConfig) -> str:
    _, dockerPath, _ = command(["which", "docker"], ignoreStdout = True, ignoreStderr = True)
    bashScriptTemplatePath = RESOURCES_DIR / "update_script_template.sh"

    with bashScriptTemplatePath.open("r") as scriptFile:
        bashScriptTemplate = scriptFile.read()

    return bashScriptTemplate.format(
        dockerPath = dockerPath.strip(),
        repository = "coretexai/coretex-node",
        tag = f"latest-{config.nodeImage}",
        serverUrl = config.serverUrl,
        storagePath = config.storagePath,
        nodeAccessToken = config.nodeAccessToken,
        containerName = DOCKER_CONTAINER_NAME,
        networkName = DOCKER_CONTAINER_NETWORK,
        restartPolicy = "always",
        ports = "21000:21000",
        capAdd = "SYS_PTRACE",
        ramMemory = config.nodeRam,
        swapMemory = config.nodeSwap,
        sharedMemory = config.nodeShared
    )


def dumpScript(updateScriptPath: Path, config: CLIConfig) -> None:
    with updateScriptPath.open("w") as scriptFile:
        scriptFile.write(generateUpdateScript(config))

    command(["chmod", "+x", str(updateScriptPath)], ignoreStdout = True)


def activateAutoUpdate(configDir: Path, config: CLIConfig) -> None:
    updateScriptPath = CONFIG_DIR / UPDATE_SCRIPT_NAME
    dumpScript(updateScriptPath, config)

    if not jobExists(UPDATE_SCRIPT_NAME):
        scheduleJob(configDir, UPDATE_SCRIPT_NAME)


def getNodeStatus() -> NodeStatus:
    try:
        response = requests.get(f"http://localhost:21000/status", timeout = 1)
        status = response.json()["status"]
        return NodeStatus(status)
    except:
        return NodeStatus.inactive
