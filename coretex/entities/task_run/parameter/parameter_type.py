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

from enum import Enum


class ParameterType(Enum):

    # Single value parameters
    integer           = "int"
    floatingPoint     = "float"
    string            = "str"
    boolean           = "bool"
    dataset           = "dataset"
    model             = "model"
    imuVectors        = "IMUVectors"
    enum              = "enum"
    range             = "range"
    awsSecret         = "aws-secret"
    gitSecret         = "git-secret"
    credentialsSecret = "credentials-secret"

    # List parameters
    intList               = "list[int]"
    floatList             = "list[float]"
    strList               = "list[str]"
    datasetList           = "list[dataset]"
    modelList             = "list[model]"
    enumList              = "list[enum]"
    awsSecretList         = "list[aws-secret]"
    gitSecretList         = "list[git-secret]"
    credentialsSecretList = "list[credentials-secret]"
