#     Copyright (C) 2023  Coretex LLC

#     This file is part of Coretex.ai

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.

#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Optional
from pathlib import Path

import click
import webbrowser

from ..modules import ui
from ..modules import task as task_utils
from ..modules.project_utils import getProject
from ..modules.user import initializeUserSession
from ..modules.utils import onBeforeCommandExecute
from ..._folder_manager import folder_manager
from ..._task import TaskRunWorker, executeRunLocally, readTaskConfig, runLogger
from ...configuration import UserConfiguration
from ...entities import Task, TaskRun, TaskRunStatus
from ...resources import PYTHON_ENTRY_POINT_PATH


class RunException(Exception):
    pass


@click.command()
@click.argument("path", type = click.Path(exists = True, dir_okay = False))
@click.option("--name", type = str, default = None)
@click.option("--description", type = str, default = None)
@click.option("--snapshot", type = bool, default = False)
@click.option("--project", "-p", type = str)
def run(path: str, name: Optional[str], description: Optional[str], snapshot: bool, project: Optional[str]) -> None:
    userConfig = UserConfiguration.load()

    if userConfig.refreshToken is None:
        raise RunException(f"Failed to execute \"coretex run {path}\" command. Authenticate again using \"coretex login\" command and try again.")

    parameters = readTaskConfig()

    # clearing temporary files in case that local run was manually killed before
    folder_manager.clearTempFiles()

    selectedProject = getProject(project, userConfig)

    if selectedProject is None:
        return

    ui.stdEcho(
        "Project info: "
        f"\n\tName: {selectedProject.name}"
        f"\n\tProject type: {selectedProject.projectType.name}"
        f"\n\tDescription: {selectedProject.description}"
        f"\n\tCreated on: {selectedProject.createdOn}"
    )

    taskRun: TaskRun = TaskRun.runLocal(
        selectedProject.id,
        snapshot,
        name,
        description,
        [parameter.encode() for parameter in parameters],
        entryPoint = path
    )

    ui.stdEcho(
        "Task Run successfully started. "
        f"You can open it by clicking on this URL {ui.outputUrl(userConfig.frontendUrl, taskRun.entityUrl())}."
    )
    webbrowser.open(f"{userConfig.frontendUrl}/{taskRun.entityUrl()}")

    taskRun.updateStatus(TaskRunStatus.preparingToStart)

    with TaskRunWorker(userConfig.refreshToken, taskRun.id):
        runLogger.attach(taskRun.id)

        command = [
            "python", str(PYTHON_ENTRY_POINT_PATH),
            "--taskRunId", str(taskRun.id),
            "--refreshToken", userConfig.refreshToken
        ]

        returnCode = executeRunLocally(
            command,
            captureErr = True
        )

    # Flush logs before updating status to a final one
    # as that invalidates the auth token
    runLogger.flushLogs()
    runLogger.reset()

    if returnCode != 0:
        runLogger.fatal(f">> [Coretex] Failed to execute Task. Exit code: {returnCode}")
        taskRun.updateStatus(TaskRunStatus.completedWithError)
    else:
        taskRun.updateStatus(TaskRunStatus.completedWithSuccess)

    folder_manager.clearTempFiles()


@click.command()
@click.argument("id", type = int, default = None)
def pull(id: int) -> None:
    initialMetadataPath = Path(f"{id}/.metadata.json")
    coretexMetadataPath = Path(f"{id}/.coretex.json")

    task = Task.fetchById(id)
    task.pull()
    task_utils.createMetadata(initialMetadataPath, coretexMetadataPath)
    task_utils.fillTaskMetadata(task, initialMetadataPath, coretexMetadataPath)


@click.group()
@onBeforeCommandExecute(initializeUserSession)
def task() -> None:
    pass


task.add_command(run, "run")
task.add_command(pull, "pull")