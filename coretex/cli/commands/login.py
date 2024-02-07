import click

from ..config import CLIConfig
from ..modules.user import authenticate
from ..modules.ui import clickPrompt, stdEcho, successEcho
from ..modules.node import DEFAULT_STORAGE_PATH


@click.command()
def login() -> None:
    config = CLIConfig.load()

    if config.isUserValid():
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
    config.storagePath = DEFAULT_STORAGE_PATH

    config.save()

    successEcho(f"User {loginInfo.username} successfully logged in.")
