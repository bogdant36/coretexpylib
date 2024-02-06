import shutil

from ..resources import RESOURCES_DIR
from ...configuration import CONFIG_DIR


NGINX_DIR = CONFIG_DIR / "nginx"


def generateConfigFiles() -> None:
    nginxFolderPath = CONFIG_DIR / "nginx"
    nginxFolderPath.mkdir(parents=True, exist_ok=True)

    nodeConfigTemplatePath = RESOURCES_DIR / "node_template.conf"
    nginxConfigTemplatePath = RESOURCES_DIR / "nginx_template.conf"

    shutil.copy(nodeConfigTemplatePath, nginxFolderPath / "node.conf")
    shutil.copy(nginxConfigTemplatePath, nginxFolderPath / "nginx.conf")
