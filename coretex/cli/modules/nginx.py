from ..resources import RESOURCES_DIR
from ...utils import command
from ...configuration import CONFIG_DIR


def start(certPath: str, keyPath: str) -> None:
    nginxCommand = [
        "nginx",
        "-g", "daemon off;",
        "-c", "path/to/nginx.conf",
        "--cert", certPath,
        "--key", keyPath
    ]

    command(nginxCommand)


def generateNodeConf() -> None:
    nginxFolderPath = CONFIG_DIR / "nginx"

    if not nginxFolderPath.exists():
        nginxFolderPath.mkdir()

    nodeConfigPath = RESOURCES_DIR / "node.conf"

    with nodeConfigPath.open("r") as nodeConfig:
        configData = nodeConfig.read()
        nodeConfigFinalPath = nginxFolderPath / "node.conf"

        with nodeConfigFinalPath.open("w") as finalNodeConfig:
            finalNodeConfig.write(configData)


def generateNginxConf() -> None:
    nginxFolderPath = CONFIG_DIR / "nginx"

    if not nginxFolderPath.exists():
        nginxFolderPath.mkdir()

    nginxConfigPath = RESOURCES_DIR / "nginx.conf"

    with nginxConfigPath.open("r") as nginxConfig:
        configData = nginxConfig.read()
        nginxConfigFinalPath = nginxFolderPath / "nginx.conf"

        with nginxConfigFinalPath.open("w") as finalNginxConfig:
            finalNginxConfig.write(configData)
