from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

import json
import platform

from .process import command, CommandException
from ..statistics import getTotalSwapMemory


def isDockerAvailable(verbose: Optional[bool] = False) -> None:
    try:
        # Run the command to check if Docker exists and is available
        command(["docker", "ps"], ignoreStdout = not verbose, ignoreStderr = True)
    except CommandException:
        raise RuntimeError("Docker not available. Please check that it is properly installed and running on your system.")


def networkExists(name: str, verbose: Optional[bool] = False) -> bool:
    # This function inspects the specified Docker network using the
    # 'docker network inspect' command. If the command exits with a return code
    # of 0, indicating success, the function returns True, meaning the network exists.
    # If the command exits with a non-zero return code, indicating failure,
    # the function returns False, meaning the network doesn't exist.
    try:
        command(["docker", "network", "inspect", name], ignoreStdout = not verbose, ignoreStderr = True)
        return True
    except:
        return False


def containerRunning(name: str, verbose: Optional[bool] = False) -> bool:
    try:
        _, output, _ = command(["docker", "ps", "--format", "{{.Names}}"], ignoreStdout = not verbose, ignoreStderr = True)
        return name in output.splitlines()
    except:
        return False


def containerExists(name: str, verbose: Optional[bool] = False) -> bool:
    try:
        _, output, _ = command(["docker", "ps", "-a", "--format", "{{.Names}}"], ignoreStdout = not verbose, ignoreStderr = True)
        return name in output.splitlines()
    except:
        return False


def createNetwork(name: str, verbose: Optional[bool] = False) -> None:
    if networkExists(name):
        removeNetwork(name)

    command(["docker", "network", "create", "--driver", "bridge", name], ignoreStdout = not verbose)


def removeNetwork(name: str, verbose: Optional[bool] = False) -> None:
    command(["docker", "network", "rm", name], ignoreStdout = not verbose, ignoreStderr = True)


def removeImage(image: str, verbose: Optional[bool] = False) -> None:
    command(["docker", "image", "rm", image], ignoreStdout = not verbose, ignoreStderr = True)


def removeDanglingImages(repository: str, tag: str, verbose: Optional[bool] = False) -> None:
    _, output, _ = command(["docker", "image", "ls", repository, "--format", "json"], ignoreStdout = not verbose, ignoreStderr = True)
    images = output.strip().split("\n")

    for image in images:
        if len(image) == 0:
            continue

        jsonImg = json.loads(image)
        if jsonImg["Tag"] != tag:
            removeImage(jsonImg["ID"])


def imagePull(image: str, verbose: Optional[bool] = False) -> None:
    command(["docker", "image", "pull", image], ignoreStdout = not verbose)


def start(
    name: str,
    image: str,
    allowGpu: bool,
    ram: int,
    swap: int,
    shm: int,
    cpuCount: int,
    environ: Dict[str, str],
    volumes: List[Tuple[str, str]],
    verbose: Optional[bool] = False
) -> None:

    # https://github.com/moby/moby/issues/14215#issuecomment-115959661
    # --memory-swap = total memory limit -> memory + swap

    runCommand = [
        "docker", "run", "-d",
        "--restart", 'always',
        "-p", "21000:21000",
        "--cap-add", "SYS_PTRACE",
        "--network", name,
        "--memory", f"{ram}G",
        "--memory-swap", f"{ram + swap}G",
        "--shm-size", f"{shm}G",
        "--cpus", f"{cpuCount}",
        "--name", name,
    ]

    for key, value in environ.items():
        runCommand.extend(["--env", f"{key}={value}"])

    for source, destination in volumes:
        runCommand.extend(["-v", f"{source}:{destination}"])

    if allowGpu:
        runCommand.extend(["--gpus", "all"])

    # Docker image must always be the last parameter of docker run command
    runCommand.append(image)
    command(runCommand, ignoreStdout = not verbose, ignoreStderr = True)


def stopContainer(name: str, verbose: Optional[bool] = False) -> None:
    command(["docker", "stop", name], ignoreStdout = not verbose, ignoreStderr = True)


def removeContainer(name: str, verbose: Optional[bool] = False) -> None:
    command(["docker", "rm", name], ignoreStdout = not verbose, ignoreStderr = True)


def manifestInspect(image: str, verbose: Optional[bool] = False) -> Dict[str, Any]:
    _, output, _ = command(["docker", "manifest", "inspect", image, "--verbose"], ignoreStdout = not verbose)
    jsonOutput = json.loads(output)
    if not isinstance(jsonOutput, dict):
        raise TypeError(f"Invalid function result type \"{type(jsonOutput)}\". Expected: \"dict\"")

    return jsonOutput


def imageInspect(image: str, verbose: Optional[bool] = False) -> Dict[str, Any]:
    _, output, _ = command(["docker", "image", "inspect", image], ignoreStdout = not verbose, ignoreStderr = True)
    jsonOutput = json.loads(output)
    if not isinstance(jsonOutput, list):
        raise TypeError(f"Invalid json.loads() result type \"{type(jsonOutput)}\". Expected: \"list\"")

    if not isinstance(jsonOutput[0], dict):  # Since we are inspecting image with specific repository AND tag output will be a list with single object
        raise TypeError(f"Invalid function result type \"{type(jsonOutput[0])}\". Expected: \"dict\"")

    return jsonOutput[0]


def getResourceLimits(verbose: Optional[bool] = False) -> Tuple[int, int]:
    _, output, _ = command(["docker", "info", "--format", "{{json .}}"], ignoreStdout = not verbose, ignoreStderr = True)
    jsonOutput = json.loads(output)

    return jsonOutput["NCPU"], round(jsonOutput["MemTotal"] / (1024 ** 3))


def getDockerConfigPath() -> Optional[Path]:
    if platform.system() == "Darwin":
        return Path.home().joinpath("Library", "Group Containers", "group.com.docker", "settings.json")
    elif platform.system() == "Windows":
        return Path.home().joinpath("AppData", "Roaming", "Docker", "settings.json")
    elif platform.system() == "Linux":
        return Path.home().joinpath(".docker", "desktop", "settings.json")
    else:
        return None


def getDockerSwapLimit() -> int:
    configPath = getDockerConfigPath()

    if configPath is None or not configPath.exists():
        return getTotalSwapMemory()

    with configPath.open("r") as configFile:
        configJson = json.load(configFile)

    swapLimit = configJson.get("swapMiB")
    if not isinstance(swapLimit, int):
        return getTotalSwapMemory()

    return int(swapLimit / 1024)
