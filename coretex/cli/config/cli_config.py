from typing import Any, Dict

from ..modules.node_mode import NodeMode


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

    def save(self) -> None:
        return

    def load(self) -> Dict[str, Any]:
        return {"lala": 0}
