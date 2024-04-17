#     Copyright (C) 2023  Coretex LLC

#     This file is part of Coretex.ai

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.

#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Dict, Any, Optional
from pathlib import Path

import os

from .base import BaseConfiguration, CONFIG_DIR
from ..utils import isCliRuntime


def getEnvVar(key: str, default: str) -> str:
    if os.environ.get(key) is None:
        return default

    return os.environ[key]


NODE_CONFIG_PATH = CONFIG_DIR / "node_config.json"
NODE_DEFAULT_CONFIG = {
    "nodeName": os.environ.get("CTX_NODE_NAME"),
    "nodeAccessToken": None,
    "storagePath": getEnvVar("CTX_STORAGE_PATH", "~/.coretex"),
    "image": "coretexai/coretex-node:latest-cpu",
    "allowGpu": False,
    "nodeRam": None,
    "nodeSharedMemory": None,
    "cpuCount": None,
    "nodeMode": None,
    "allowDocker": False,
    "nodeSecret": None,
    "initScript": None,
    "modelId": None,
}


class InvalidNodeConfiguration(Exception):
    pass


class NodeConfiguration(BaseConfiguration):

    def __init__(self) -> None:
        super().__init__(NODE_CONFIG_PATH)
        nodeSecret = self.nodeSecret
        if isinstance(nodeSecret, str) and nodeSecret != "":
            os.environ["CTX_SECRETS_KEY"] = nodeSecret

        if not isCliRuntime():
            os.environ["CTX_STORAGE_PATH"] = self.storagePath
        else:
            os.environ["CTX_STORAGE_PATH"] = f"{CONFIG_DIR}/data"

    @classmethod
    def getDefaultConfig(cls) -> Dict[str, Any]:
        return NODE_DEFAULT_CONFIG

    @property
    def nodeName(self) -> str:
        return self.getValue("nodeName", str, "CTX_NODE_NAME")

    @nodeName.setter
    def nodeName(self, value: str) -> None:
        self._raw["nodeName"] = value

    @property
    def nodeAccessToken(self) -> str:
        return self.getValue("nodeAccessToken", str)

    @nodeAccessToken.setter
    def nodeAccessToken(self, value: str) -> None:
        self._raw["nodeAccessToken"] = value

    @property
    def storagePath(self) -> str:
        return self.getValue("storagePath", str, "CTX_STORAGE_PATH")

    @storagePath.setter
    def storagePath(self, value: Optional[str]) -> None:
        self._raw["storagePath"] = value

    @property
    def image(self) -> str:
        return self.getValue("image", str)

    @image.setter
    def image(self, value: str) -> None:
        self._raw["image"] = value

    @property
    def allowGpu(self) -> bool:
        return self.getValue("allowGpu", bool)

    @allowGpu.setter
    def allowGpu(self, value: bool) -> None:
        self._raw["allowGpu"] = value

    @property
    def nodeRam(self) -> int:
        return self.getValue("nodeRam", int)

    @nodeRam.setter
    def nodeRam(self, value: int) -> None:
        self._raw["nodeRam"] = value

    @property
    def nodeSwap(self) -> int:
        return self.getValue("nodeSwap", int)

    @nodeSwap.setter
    def nodeSwap(self, value: int) -> None:
        self._raw["nodeSwap"] = value

    @property
    def nodeSharedMemory(self) -> int:
        return self.getValue("nodeSharedMemory", int)

    @nodeSharedMemory.setter
    def nodeSharedMemory(self, value: int) -> None:
        self._raw["nodeSharedMemory"] = value

    @property
    def cpuCount(self) -> int:
        return self.getValue("cpuCount", int)

    @cpuCount.setter
    def cpuCount(self, value: int) -> None:
        self._raw["cpuCount"] = value

    @property
    def nodeMode(self) -> int:
        return self.getValue("nodeMode", int)

    @nodeMode.setter
    def nodeMode(self, value: int) -> None:
        self._raw["nodeMode"] = value

    @property
    def allowDocker(self) -> bool:
        return self.getValue("allowDocker", bool)

    @allowDocker.setter
    def allowDocker(self, value: bool) -> None:
        self._raw["allowDocker"] = value

    @property
    def nodeSecret(self) -> Optional[str]:
        return self.getOptValue("nodeSecret", str)

    @nodeSecret.setter
    def nodeSecret(self, value: Optional[str]) -> None:
        self._raw["nodeSecret"] = value

    @property
    def initScript(self) -> Optional[str]:
        return self.getOptValue("initScript", str)

    @initScript.setter
    def initScript(self, value: Optional[str]) -> None:
        self._raw["initScript"] = value

    @property
    def modelId(self) -> Optional[int]:
        return self.getOptValue("modelId", int)

    @modelId.setter
    def modelId(self, value: Optional[int]) -> None:
        self._raw["modelId"] = value

    def isNodeConfigured(self) -> bool:
        isConfigured = True
        if self._raw.get("nodeName") is None or isinstance("nodeName", str):
            isConfigured = False

        if self._raw.get("password") is None or isinstance("password", str):
            isConfigured = False

        if self._raw.get("image") is None or isinstance("image", str):
            isConfigured = False

        if self._raw.get("nodeAccessToken") is None or isinstance("nodeAccessToken", str):
            isConfigured = False

        if self._raw.get("nodeRam") is None or isinstance("nodeRam", int):
            isConfigured = False

        if self._raw.get("nodeSwap") is None or isinstance("nodeSwap", int):
            isConfigured = False

        if self._raw.get("nodeSharedMemory") is None or isinstance("nodeSharedMemory", int):
            isConfigured = False

        if self._raw.get("nodeMode") is None or isinstance("nodeMode", int):
            isConfigured = False

        return isConfigured

    def getInitScriptPath(self) -> Optional[Path]:
        value = self._raw.get("initScript")

        if not isinstance(value, str):
            return None

        if value == "":
            return None

        path = Path(value).expanduser().absolute()
        if not path.exists():
            return None

        return path