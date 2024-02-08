from datetime import datetime, timezone

from .ui import clickPrompt, errorEcho, progressEcho
from ..config import CLIConfig
from ...utils import decodeDate
from ...networking import networkManager, NetworkResponse, NetworkRequestError
from ..config.login_info import LoginInfo

def authenticateUser(username: str, password: str) -> NetworkResponse:
    response = networkManager.authenticate(username, password, False)

    if response.hasFailed():
        if response.statusCode >= 500:
            raise NetworkRequestError(response, "Something went wrong, please try again later.")

        if response.statusCode >= 400:
            raise NetworkRequestError(response, "User credentials invalid, please try configuring them again.")

    return response


def authenticate(retryCount: int = 0) -> LoginInfo:
    if retryCount >= 3:
        raise RuntimeError("Failed to authenticate. Terminating...")

    username = clickPrompt("Email", type = str)
    password = clickPrompt("Password", type = str, hide_input = True)

    progressEcho("Authenticating...")
    response = networkManager.authenticate(username, password, False)

    if response.hasFailed():
        errorEcho("Failed to authenticate. Please try again...")
        return authenticate(retryCount + 1)

    jsonResponse = response.getJson(dict)

    return LoginInfo(
        username,
        password,
        jsonResponse["token"],
        jsonResponse["expires_on"],
        jsonResponse["refresh_token"],
        jsonResponse["refresh_expires_on"]
    )


def initializeUserSession() -> None:
    config = CLIConfig.load()

    if config.username is '' or config.password is '':
        errorEcho("User configuration not found. Please authenticate with your credentials.")
        loginInfo = authenticate()
        config.saveLoginData(loginInfo)
    else:
        if config.tokenExpirationDate is not '' and config.refreshTokenExpirationDate is not '':
            tokenExpirationDate = decodeDate(config.tokenExpirationDate)
            refreshTokenExpirationDate = decodeDate(config.refreshTokenExpirationDate)

            currentDate = datetime.utcnow().replace(tzinfo = timezone.utc)

            if currentDate < tokenExpirationDate:
                return

            if currentDate < refreshTokenExpirationDate:
                refreshToken = config.refreshToken
                response = networkManager.authenticateWithRefreshToken(refreshToken)
                if response.hasFailed():
                    if response.statusCode >= 500:
                        raise NetworkRequestError(response, "Something went wrong, please try again later.")

                    if response.statusCode >= 400:
                        response = authenticateUser(config.username, config.password)
            else:
                response = authenticateUser(config.username, config.password)
        else:
            response = authenticateUser(config.username, config.password)

        jsonResponse = response.getJson(dict)
        config.token = jsonResponse["token"]
        config.tokenExpirationDate = jsonResponse["expires_on"]
        config.refreshToken = jsonResponse.get("refresh_token", config.refreshToken)
        config.refreshTokenExpirationDate = jsonResponse.get("refresh_expires_on", config.refreshTokenExpirationDate)

    config.save()

