import click

from ..config import CLIConfig
from ..modules.user import authenticate, saveLoginData
from ..modules.ui import clickPrompt, stdEcho, successEcho
from ...configuration import loadConfig, saveConfig, isUserConfigured


@click.command()
def login() -> None:
    config = CLIConfig()
    if config.verifyUser():
        if not clickPrompt(
            f"User already logged in with username {config.username}.\nWould you like to log in with a different user (Y/n)?",
            type = bool,
            default = True,
            show_default = False
        ):
            return

    stdEcho("Please enter your credentials:")
    loginInfo = authenticate()
    config.saveLoginData(loginInfo)

    config.save()

    successEcho(f"User {loginInfo.username} successfully logged in.")
