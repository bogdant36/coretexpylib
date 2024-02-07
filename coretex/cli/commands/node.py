import click

from ..config import CLIConfig
from ..resources import UPDATE_SCRIPT_NAME
from ..modules import node as node_module
from ..modules.ui import clickPrompt, successEcho, errorEcho
from ..modules.update import NodeStatus, getNodeStatus, activateAutoUpdate, dumpScript, UPDATE_SCRIPT_NAME
from ..modules.utils import onBeforeCommandExecute
from ..modules.user import initializeUserSession
from ..modules.docker import isDockerAvailable
from ...configuration import CONFIG_DIR


@click.command()
@onBeforeCommandExecute(node_module.initializeNodeConfiguration)
def start() -> None:
    config = CLIConfig.load()
    repository = "coretexai/coretex-node"
    tag = f"latest-{config.nodeImage}"

    if node_module.isRunning():
        if not clickPrompt(
            "Node is already running. Do you wish to restart the Node? (Y/n)",
            type = bool,
            default = True,
            show_default = False
        ):
            return

        node_module.stop(config.isHTTPS)

    if node_module.shouldUpdate(repository, tag):
        node_module.pull("coretexai/coretex-node", f"latest-{config.nodeImage}")

    node_module.start(f"{repository}:{tag}", config)

    activateAutoUpdate(CONFIG_DIR, config)


@click.command()
def stop() -> None:
    config = CLIConfig.load()
    if not node_module.isRunning():
        errorEcho("Node is already offline.")
        return

    node_module.stop(config.isHTTPS)


@click.command
@onBeforeCommandExecute(node_module.initializeNodeConfiguration)
def update() -> None:
    config = CLIConfig.load()
    repository = "coretexai/coretex-node"
    tag = f"latest-{config.nodeImage}"

    nodeStatus = getNodeStatus()

    if nodeStatus == NodeStatus.inactive:
        errorEcho("Node is not running. To update Node you need to start it first.")
        return

    if nodeStatus == NodeStatus.reconnecting:
        errorEcho("Node is reconnecting. Cannot update now.")
        return

    if nodeStatus == NodeStatus.busy:
        if not clickPrompt(
            "Node is busy, do you wish to terminate the current execution to perform the update? (Y/n)",
            type = bool,
            default = True,
            show_default = False
        ):
            return

        node_module.stop(config.isHTTPS)

    if not node_module.shouldUpdate(repository, tag):
        successEcho("Node is already up to date.")
        return

    node_module.pull(repository, tag)

    if getNodeStatus() == NodeStatus.busy:
        if not clickPrompt(
            "Node is busy, do you wish to terminate the current execution to perform the update? (Y/n)",
            type = bool,
            default = True,
            show_default = False
        ):
            return

    node_module.stop(config.isHTTPS)

    node_module.start(f"{repository}:{tag}", config)


@click.command()
@click.option("--verbose", is_flag = True, help = "Configure node settings manually.")
def config(verbose: bool) -> None:
    config = CLIConfig.load()

    if node_module.isRunning():
        if not clickPrompt(
            "Node is already running. Do you wish to stop the Node? (Y/n)",
            type = bool,
            default = True,
            show_default = False
        ):
            errorEcho("If you wish to reconfigure your node, use coretex node stop commands first.")
            return

        node_module.stop(config.isHTTPS)

    if config.isNodeValid():
        if not clickPrompt(
            "Node configuration already exists. Would you like to update? (Y/n)",
            type = bool,
            default = True,
            show_default = False
        ):
            return

    node_module.configureNode(config, verbose)
    config.save()
    config.previewConfig()

    # Updating auto-update script since node configuration is changed
    dumpScript(CONFIG_DIR / UPDATE_SCRIPT_NAME, config)

    successEcho("Node successfully configured.")


@click.group()
@onBeforeCommandExecute(isDockerAvailable)
@onBeforeCommandExecute(initializeUserSession)
def node() -> None:
    pass


node.add_command(start, "start")
node.add_command(stop, "stop")
node.add_command(update, "update")
node.add_command(config, "config")
