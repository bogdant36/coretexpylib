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

from pathlib import Path

import os
import json


def getEnvVar(key: str, default: str) -> str:
    if os.environ.get(key) is None:
        os.environ[key] = default

    return os.environ[key]


def _syncConfigWithEnv() -> None:
    userConfigPath = Path.home().joinpath(".config", "coretex", "user_config.json")
    nodeConfigPath = Path.home().joinpath(".config", "coretex", "node_config.json")

    if not "CTX_API_URL" in os.environ:
        if not userConfigPath.exists():
            os.environ["CTX_API_URL"] = "https://api.coretex.ai/"
        else:
            with userConfigPath.open("r") as userConfigFile:
                userConfig = json.load(userConfigFile)
                if isinstance(userConfig, dict):
                    os.environ["CTX_API_URL"] = userConfig.get("serverUrl", "https://api.coretex.ai/")

    if not "CTX_STORAGE_PATH" in os.environ:
        if not nodeConfigPath.exists():
            os.environ["CTX_STORAGE_PATH"] = "~/.coretex"
        else:
            with nodeConfigPath.open("r") as nodeConfigFile:
                nodeConfig = json.load(nodeConfigFile)
                if isinstance(nodeConfig, dict):
                    os.environ["CTX_STORAGE_PATH"] = nodeConfig.get("storagePath", "~/.coretex")
