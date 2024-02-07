from typing import Optional, List, Any
from typing_extensions import Self
from pathlib import Path

import os
import json

from coretex.cli.modules.node_mode import NodeMode
from coretex.cli.modules.ui import stdEcho

from tabulate import tabulate

from .utils import typedGet
from .login_info import LoginInfo


CONFIG_DIR = Path.home().joinpath(".config", "coretex")
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.json"


class CLIConfig():

    def __init__(self) -> None:
        self.serverUrl: str = "https://devext.biomechservices.com:29007/"

        self.username: Optional[str] = None
        self.password: Optional[str] = None

        self.token: Optional[str] = None
        self.refreshToken: Optional[str] = None
        self.tokenExpirationDate: Optional[str] = None
        self.refreshTokenExpirationDate: Optional[str] = None

        self.nodeName: Optional[str] = None
        self.nodeAccessToken: Optional[str] = None
        self.nodeImage: Optional[str] = None
        self.nodeRam: Optional[int] = None
        self.nodeSwap: Optional[int] = None
        self.nodeShared: Optional[int] = None
        self.nodeMode: Optional[int] = None
        self.modelId: Optional[int] = None

        self.isHTTPS: Optional[bool] = None
        self.certPemPath: Optional[str] = None
        self.keyPemPath: Optional[str] = None

        self.storagePath: Optional[str] = None
        self.projectId: Optional[int] = None

    @classmethod
    def load(cls) -> Self:
        with open(DEFAULT_CONFIG_PATH, "r") as configFile:
            config = json.load(configFile)

        if not isinstance(config, dict):
            raise TypeError(f">> Invalid config type \"{type(config)}\", expected \"dict\"")

        self = cls()

        serverUrl = config.get("serverUrl", os.environ["CTX_API_URL"])
        if not isinstance(serverUrl, str):
            serverUrl = "https://devext.biomechservices.com:29007/"

        self.serverUrl = serverUrl
        self.username = typedGet(config, "username", str)
        self.password = typedGet(config, "password", str)

        self.token = typedGet(config, "token", str)
        self.refreshToken = typedGet(config, "refreshToken", str)
        self.tokenExpirationDate = typedGet(config, "tokenExpirationDate", str)
        self.refreshTokenExpirationDate = typedGet(config, "refreshTokenExpirationDate", str)

        self.nodeName = typedGet(config, "nodeName", str)
        self.nodeImage = typedGet(config, "nodeImage", str)
        self.nodeRam = typedGet(config, "nodeRam", int)
        self.nodeSwap = typedGet(config, "nodeSwap", int)
        self.nodeShared = typedGet(config, "nodeShared", int)
        self.nodeMode = typedGet(config, "nodeMode", int)
        self.modelId = typedGet(config, "modelId", int)

        self.isHTTPS = typedGet(config, "isHTTPS", bool)
        self.certPemPath = typedGet(config, "certPemPath", str)
        self.keyPemPath = typedGet(config, "keyPemPath", str)

        self.storagePath = typedGet(config, "storagePath", str)
        self.projectId = typedGet(config, "projectId", int)

        return self

    def save(self) -> None:
        config = vars(self)
        print(config)
        with open(DEFAULT_CONFIG_PATH, "w+") as configFile:
            json.dump(config, configFile, indent=4)

    def isUserValid(self) -> bool:
        return (
            self.username is not None
            and self.password is not None
        )

    def isNodeValid(self) -> bool:
        return (
            self.username is not None and
            self.storagePath is not None and
            self.nodeImage is not None and
            self.serverUrl is not None and
            self.nodeName is not None and
            self.nodeAccessToken is not None and
            self.nodeRam is not None and
            self.nodeSwap is not None and
            self.nodeShared is not None and
            self.nodeMode is not None
        )

    def saveLoginData(self, loginInfo: LoginInfo) -> None:
        self.username = loginInfo.username
        self.password = loginInfo.password
        self.token = loginInfo.token
        self.tokenExpirationDate = loginInfo.tokenExpirationDate
        self.refreshToken = loginInfo.refreshToken
        self.refreshToken = loginInfo.refreshTokenExpirationDate


    def previewConfig(self) -> None:
        table: List[List[Any]] = [
            ["Node name", self.nodeName],
            ["Server URL", self.serverUrl],
            ["Storage path", self.storagePath],
            ["RAM", f"{self.nodeRam}GB"],
            ["SWAP memory", f"{self.nodeSwap}GB"],
            ["POSIX shared memory", f"{self.nodeShared}GB"],
        ]
        if self.modelId is not None:
            table.append(["Coretex Model ID", str(self.modelId)])

        if self.nodeMode is not None:
            table.append(["Node mode", f"{NodeMode(self.nodeMode).name}"])

        stdEcho(tabulate(table, tablefmt = "grid"))
