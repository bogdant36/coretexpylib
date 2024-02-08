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

        self._username: Optional[str] = None
        self._password: Optional[str] = None

        self._token: Optional[str] = None
        self._refreshToken: Optional[str] = None
        self._tokenExpirationDate: Optional[str] = None
        self._refreshTokenExpirationDate: Optional[str] = None

        self._nodeName: Optional[str] = None
        self._nodeAccessToken: Optional[str] = None
        self._nodeImage: Optional[str] = None
        self._nodeRam: Optional[int] = None
        self._nodeSwap: Optional[int] = None
        self._nodeShared: Optional[int] = None
        self._nodeMode: Optional[int] = None
        self._modelId: Optional[int] = None

        self._isHTTPS: Optional[bool] = None
        self.certPemPath: Optional[str] = None
        self.keyPemPath: Optional[str] = None

        self._storagePath: Optional[str] = None
        self.projectId: Optional[int] = None

    @property
    def username(self) -> str:
        if self._username is None:
            return ''
        return self._username

    @username.setter
    def username(self, value: Optional[str]) -> None:
        self._username = value

    @property
    def password(self) -> str:
        if self._password is None:
            return ''
        return self._password

    @password.setter
    def password(self, value: Optional[str]) -> None:
        self._password = value

    @property
    def token(self) -> str:
        if self._token is None:
            return ''
        return self._token

    @token.setter
    def token(self, value: Optional[str]) -> None:
        self._token = value

    @property
    def tokenExpirationDate(self) -> str:
        if self._tokenExpirationDate is None:
            return ''
        return self._tokenExpirationDate

    @tokenExpirationDate.setter
    def tokenExpirationDate(self, value: Optional[str]) -> None:
        self._tokenExpirationDate = value

    @property
    def refreshToken(self) -> str:
        if self._refreshToken is None:
            return ''
        return self._refreshToken

    @refreshToken.setter
    def refreshToken(self, value: Optional[str]) -> None:
        self._refreshToken = value

    @property
    def refreshTokenExpirationDate(self) -> str:
        if self._refreshTokenExpirationDate is None:
            return ''
        return self._refreshTokenExpirationDate

    @refreshTokenExpirationDate.setter
    def refreshTokenExpirationDate(self, value: Optional[str]) -> None:
        self._refreshTokenExpirationDate = value

    @property
    def nodeName(self) -> str:
        if self._nodeName is None:
            return ''
        return self._nodeName

    @nodeName.setter
    def nodeName(self, value: Optional[str]) -> None:
        self._nodeName = value

    @property
    def nodeAccessToken(self) -> str:
        if self._nodeAccessToken is None:
            return ''
        return self._nodeAccessToken

    @nodeAccessToken.setter
    def nodeAccessToken(self, value: Optional[str]) -> None:
        self._nodeAccessToken = value

    @property
    def nodeImage(self) -> str:
        if self._nodeImage is None:
            return "cpu"
        return self._nodeImage

    @nodeImage.setter
    def nodeImage(self, value: Optional[str]) -> None:
        self._nodeImage = value

    @property
    def nodeRam(self) -> int:
        if self._nodeRam is None:
            return 1
        return self._nodeRam

    @nodeRam.setter
    def nodeRam(self, value: Optional[int]) -> None:
        self._nodeRam = value

    @property
    def nodeSwap(self) -> int:
        if self._nodeSwap is None:
            return 1
        return self._nodeSwap

    @nodeSwap.setter
    def nodeSwap(self, value: Optional[int]) -> None:
        self._nodeSwap = value

    @property
    def nodeShared(self) -> int:
        if self._nodeShared is None:
            return 1
        return self._nodeShared

    @nodeShared.setter
    def nodeShared(self, value: Optional[int]) -> None:
        self._nodeShared = value

    @property
    def nodeMode(self) -> int:
        if self._nodeMode is None:
            return NodeMode.execution
        return self._nodeMode

    @nodeMode.setter
    def nodeMode(self, value: Optional[int]) -> None:
        self._nodeMode = value

    @property
    def modelId(self) -> int:
        if self._modelId is None:
            return 1
        return self._modelId

    @modelId.setter
    def modelId(self, value: Optional[int]) -> None:
        self._modelId = value

    @property
    def isHTTPS(self) -> bool:
        if self._isHTTPS is None:
            return False
        return self._isHTTPS

    @isHTTPS.setter
    def isHTTPS(self, value: Optional[bool]) -> None:
        self._isHTTPS = value

    @property
    def storagePath(self) -> str:
        if self._storagePath is None:
            return ''
        return self._storagePath

    @storagePath.setter
    def storagePath(self, value: Optional[str]) -> None:
        self._storagePath = value

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
        self._username = typedGet(config, "username", str)
        self._password = typedGet(config, "password", str)

        self._token = typedGet(config, "token", str)
        self._refreshToken = typedGet(config, "refreshToken", str)
        self._tokenExpirationDate = typedGet(config, "tokenExpirationDate", str)
        self._refreshTokenExpirationDate = typedGet(config, "refreshTokenExpirationDate", str)

        self._nodeName = typedGet(config, "nodeName", str)
        self._nodeImage = typedGet(config, "nodeImage", str)
        self._nodeRam = typedGet(config, "nodeRam", int)
        self._nodeSwap = typedGet(config, "nodeSwap", int)
        self._nodeShared = typedGet(config, "nodeShared", int)
        self._nodeMode = typedGet(config, "nodeMode", int)
        self._modelId = typedGet(config, "modelId", int)

        self._isHTTPS = typedGet(config, "isHTTPS", bool)
        self.certPemPath = typedGet(config, "certPemPath", str)
        self.keyPemPath = typedGet(config, "keyPemPath", str)

        self._storagePath = typedGet(config, "storagePath", str)
        self.projectId = typedGet(config, "projectId", int)

        return self

    def save(self) -> None:
        config = {
            "serverUrl": self.serverUrl,
            "username": self.username,
            "password": self.password,
            "token": self.token,
            "refreshToken": self.refreshToken,
            "tokenExpirationDate": self.tokenExpirationDate,
            "refreshTokenExpirationDate": self.refreshTokenExpirationDate,
            "nodeName": self.nodeName,
            "nodeAccessToken": self.nodeAccessToken,
            "nodeImage": self.nodeImage,
            "nodeRam": self.nodeRam,
            "nodeSwap": self.nodeSwap,
            "nodeShared": self.nodeShared,
            "nodeMode": self.nodeMode,
            "modelId": self.modelId,
            "isHTTPS": self.isHTTPS,
            "certPemPath": self.certPemPath,
            "keyPemPath": self.keyPemPath,
            "storagePath": self.storagePath,
            "projectId": self.projectId
        }

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
        self._username = loginInfo.username
        self._password = loginInfo.password
        self._token = loginInfo.token
        self._tokenExpirationDate = loginInfo.tokenExpirationDate
        self._refreshToken = loginInfo.refreshToken
        self._refreshToken = loginInfo.refreshTokenExpirationDate


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
