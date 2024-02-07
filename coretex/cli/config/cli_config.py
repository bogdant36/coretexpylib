from typing import Any, Dict
from pathlib import Path

import json

from ..modules.user import LoginInfo
from ..modules.node_mode import NodeMode
from ..modules import node as node_module


CONFIG_DIR = Path.home().joinpath(".config", "coretex")
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.json"


class CLIConfig():

    username: str
    password: str
    token: str
    refreshToken: str
    serverUrl: str
    storagePath: str
    tokenExpirationDate: str
    refreshTokenExpirationDate: str
    nodeAccessToken: str
    nodeImage: str
    nodeRam: int
    nodeSwap: int
    nodeShared: int
    nodeMode: NodeMode
    isHTTPS: bool
    certPemPath: str
    keyPemPath: str

    def __init__(self) -> None:
        self.config = self.load()
        self._updateAttributes()

    def load(self) -> Dict[str, Any]:
        with open(DEFAULT_CONFIG_PATH, "r") as configFile:
            config = json.load(configFile)

        if not isinstance(config, dict):
            raise TypeError(f">> Invalid config type \"{type(config)}\", expected \"dict\"")

        if not self._verify(config):
            raise RuntimeError(">> [Coretex] Invalid configuration")

        return config

    def save(self) -> None:
        with open(DEFAULT_CONFIG_PATH, "w+") as configFile:
            json.dump(self.config, configFile, indent=4)

    def _updateAttributes(self) -> None:
        self.username = self.config.get("username", "")
        self.password = self.config.get("password", "")
        self.token = self.config.get("token", None)
        self.refreshToken = self.config.get("refreshToken", None)
        self.serverUrl = self.config.get("serverUrl", "https://devext.biomechservices.com:29007/")
        self.storagePath = self.config.get("storagePath", node_module.DEFAULT_STORAGE_PATH)
        self.tokenExpirationDate = self.config.get("tokenExpirationDate", None)
        self.refreshTokenExpirationDate = self.config.get("refreshTokenExpirationDate", None)
        self.nodeAccessToken = self.config.get("nodeAccessToken", None)
        self.nodeImage = self.config.get("nodeImage", "cpu")
        self.nodeRam = self.config.get("nodeRam", node_module.DEFAULT_RAM_MEMORY)
        self.nodeSwap = self.config.get("nodeSwap", node_module.DEFAULT_SWAP_MEMORY)
        self.nodeShared = self.config.get("nodeShared", node_module.DEFAULT_SHARED_MEMORY)
        self.nodeMode = self.config.get("nodeMode", NodeMode.execution)
        self.isHTTPS = self.config.get("isHTTPS", False)
        self.certPemPath = self.config.get("certPemPath", None)
        self.keyPemPath = self.config.get("keyPemPath", None)

    def _verify(self, config: Dict[str, Any]) -> bool:
        return (
            config.get("username") is not None
            and config.get("password") is not None
            and config.get("storagePath") is not None
        )

    def verifyUser(self) -> bool:
        return (
            self.config.get("username") is not None
            and self.config.get("password") is not None
            and self.config.get("storagePath") is not None
        )

    def verifyNode(self) -> bool:
        return (
            self.config.get("nodeName") is not None
            and self.config.get("storagePath") is not None
            and self.config.get("image") is not None
            and self.config.get("serverUrl") is not None
            and self.config.get("nodeAccessToken") is not None
            and self.config.get("nodeRam") is not None
            and self.config.get("nodeSwap") is not None
            and self.config.get("nodeSharedMemory") is not None
        )

    def saveLoginData(self, loginInfo: LoginInfo) -> None:
        self.config["username"] = loginInfo.username
        self.config["password"] = loginInfo.password
        self.config["token"] = loginInfo.token
        self.config["tokenExpirationDate"] = loginInfo.tokenExpirationDate
        self.config["refreshToken"] = loginInfo.refreshToken
        self.config["refreshTokenExpirationDate"] = loginInfo.refreshTokenExpirationDate
