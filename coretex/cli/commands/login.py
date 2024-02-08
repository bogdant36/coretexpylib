import click

from ..config.user import UserConfiguration, InvalidUserConfiguration
from ..modules.user import userConfigurationPrompt
from ..modules.ui import clickPrompt, stdEcho, successEcho


@click.command()
def login() -> None:
    try:
        userConfig = UserConfiguration.initialize()
        if not clickPrompt(
            f"User already logged in with username {userConfig.username}.\nWould you like to log in with a different user (Y/n)?",
            type = bool,
            default = True,
            show_default = False
        ):
            return

    except InvalidUserConfiguration:
        pass

    stdEcho("Please enter your credentials:")
    userConfig = userConfigurationPrompt()
    userConfig.save()

    successEcho(f"User {userConfig.username} successfully logged in.")
