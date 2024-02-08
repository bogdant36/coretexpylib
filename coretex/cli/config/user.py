from typing import Optional
from typing_extensions import Self
from dataclasses import dataclass
from datetime import datetime, timezone

import json

from .utils import typedGet
from .login_info import LoginInfo
from .configuration import CONFIG_DIR
from ...utils import decodeDate
from ...networking import networkManager, NetworkRequestError, NetworkResponse


class InvalidUserConfiguration(Exception):
    pass


USER_CONFIG_PATH = CONFIG_DIR / "user_config.json"
DEFAULT_USER_CONFIG = {
    "username": None,
    "password": None,
    "token": None,
    "refreshToken": None,
    "tokenExpirationDate": None,
    "refreshTokenExpirationDate": None,
    "serverUrl": "https://api.coretex.ai/"
}

def authenticateUser(username: str, password: str) -> NetworkResponse:
    response = networkManager.authenticate(username, password, False)

    if response.hasFailed():
        if response.statusCode >= 500:
            raise NetworkRequestError(response, "Something went wrong, please try again later.")

        if response.statusCode >= 400:
            raise NetworkRequestError(response, "User credentials invalid, please try configuring them again.")

    return response


def hasExpired(tokenExpirationDate: Optional[str]) -> bool:
    if tokenExpirationDate is None:
        return False

    currentDate = datetime.utcnow().replace(tzinfo = timezone.utc)
    return currentDate >= decodeDate(tokenExpirationDate)


@dataclass
class UserConfiguration:

    username: str
    password: str
    token: str
    refreshToken: str
    tokenExpirationDate: str
    refreshTokenExpirationDate: str

    @classmethod
    def initialize(cls) -> Self:
        if not USER_CONFIG_PATH.exists():
            with USER_CONFIG_PATH.open("w") as configFile:
                json.dump(DEFAULT_USER_CONFIG, configFile, indent = 4)

        with open(USER_CONFIG_PATH, "r") as file:
            config = json.load(file)

        if not isinstance(config, dict):
            raise InvalidUserConfiguration(f"Invalid config type \"{type(config)}\", expected: \"dict\".")  # TODO : Custom error

        username = config.get("username")
        password = config.get("password")

        if username is None or password is None:
            raise InvalidUserConfiguration("User configuration missing credentials.e")

        token = config.get("token")
        refreshToken = config.get("refreshToken")
        tokenExpirationDate = config.get("tokenExpirationDate")
        refreshTokenExpirationDate = config.get("refreshTokenExpirationDate")

        if (
            not isinstance(token, str) or
            not isinstance(refreshToken, str) or
            not isinstance(tokenExpirationDate, str) or
            not isinstance(refreshTokenExpirationDate, str)
        ):
            response = authenticateUser(username, password)

            if response.statusCode >= 500:
                raise NetworkRequestError(response, "Something went wrong, please try again later.")

            if response.statusCode >= 400:
                raise InvalidUserConfiguration("Something went wrong during authentication. Please try using command \"coretex login\" again.")

            jsonResponse = response.getJson(dict)
            token = typedGet(jsonResponse, "token", str)
            refreshToken = typedGet(jsonResponse, "refresh_token", str)
            tokenExpirationDate = typedGet(jsonResponse, "expires_on", str)
            refreshTokenExpirationDate = typedGet(jsonResponse, "refresh_expires_on", str)

        return cls(
            username,
            password,
            token,
            refreshToken,
            tokenExpirationDate,
            refreshTokenExpirationDate
        )

    def save(self) -> None:
        with USER_CONFIG_PATH.open("w") as configFile:
            json.dump(self.__dict__, configFile, indent = 4)
