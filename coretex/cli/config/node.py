from typing import Optional, List, Any
from typing_extensions import Self
from dataclasses import dataclass
from pathlib import Path

import json

from tabulate import tabulate

from .configuration import CONFIG_DIR
from ..modules.ui import stdEcho
from ..modules.node_mode import NodeMode

NODE_CONFIG_PATH = CONFIG_DIR / "node_config.json"
DEFAULT_STORAGE_PATH = Path.home() / "./coretex"

DEFAULT_NODE_CONFIG = {
    "name": None,
    "accessToken": None,
    "image": None,
    "ram": None,
    "swap": None,
    "shm": None,
    "mode": None,
    "modelId": None,
    "isHTTPS": False,
    "certPemPath": None,
    "keyPemPath": None,
    "storagePath": None
}


@dataclass
class NodeConfiguration:

    name: str
    accessToken: str
    image: str
    ram: int
    swap: int
    shm: int
    mode: int
    modelId: Optional[int]
    isHTTPS: bool
    certPemPath: Optional[str]
    keyPemPath: Optional[str]
    storagePath: str

    @classmethod
    def load(cls) -> Self:
        if not NODE_CONFIG_PATH.exists():
            with NODE_CONFIG_PATH.open("w") as configFile:
                json.dump(DEFAULT_NODE_CONFIG, configFile, indent = 4)

        with open(NODE_CONFIG_PATH, "r") as file:
            config = json.load(file)

        if not isinstance(config, dict):
            raise TypeError("Invalid configuration type...")  # TODO : Custom error

        name = config.get("name")
        accessToken = config.get("accessToken")
        image = config.get("image")
        mode = config.get("mode")
        ram = config.get("ram")
        swap = config.get("swap")
        shm = config.get("shm")
        storagePath = config.get("storagePath")

        if (
            name is None or
            accessToken is None or
            image is None or
            mode is None or
            ram is None or
            swap is None or
            shm is None or
            storagePath is None
        ):
            raise Exception("invalid configuration") # TODO : Custom error

        return cls(
            name,
            accessToken,
            image,
            ram,
            swap,
            shm,
            mode,
            config.get("modelId"),
            config.get("isHTTPS", False),
            config.get("certPemPath"),
            config.get("keyPemPath"),
            storagePath,
        )

    def save(self) -> None:
        with NODE_CONFIG_PATH.open("w") as configFile:
            json.dump(self.__dict__, configFile, indent = 4)

    def previewConfig(self) -> None:
        table: List[List[Any]] = [
            ["Node name", self.name],
            ["Storage path", self.storagePath],
            ["RAM", f"{self.ram}GB"],
            ["SWAP memory", f"{self.swap}GB"],
            ["POSIX shared memory", f"{self.shm}GB"],
        ]

        if self.modelId is not None:
            table.append(["Coretex Model ID", str(self.modelId)])

        if self.mode is not None:
            table.append(["Node mode", f"{NodeMode(self.mode).name}"])

        stdEcho(tabulate(table, tablefmt = "grid"))
