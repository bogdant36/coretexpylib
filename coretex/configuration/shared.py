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

from .base import BaseConfiguration, CONFIG_DIR


class SharedConfiguration(BaseConfiguration):

    @classmethod
    def getConfigPath(cls) -> Path:
        return CONFIG_DIR / "shared_config.json"

    @property
    def serverUrl(self) -> str:
        return self.getValue("serverUrl", str, "CTX_API_URL", "https://api.coretex.ai/")

    @serverUrl.setter
    def serverUrl(self, value: str) -> None:
        self._raw["serverUrl"] = value
