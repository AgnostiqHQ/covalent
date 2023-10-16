# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import enum


class Order(str, enum.Enum):
    BEFORE = "before"
    AFTER = "after"


class FileSchemes(str, enum.Enum):
    File = "file"
    S3 = "s3"
    Blob = "https"
    GCloud = "gs"
    Globus = "globus"
    HTTP = "http"
    HTTPS = "https"
    FTP = "ftp"


class FileTransferStrategyTypes(str, enum.Enum):
    Shutil = "Shutil"
    Rsync = "rsync"
    HTTP = "http"
    S3 = "s3"
    GCloud = "gs"
    FTP = "ftp"
    GLOBUS = "globus"


SchemeToStrategyMap = {
    "file": FileTransferStrategyTypes.Shutil,
    "http": FileTransferStrategyTypes.HTTP,
    "https": FileTransferStrategyTypes.HTTP,
    "s3": FileTransferStrategyTypes.S3,
    "gs": FileTransferStrategyTypes.GCloud,
    "ftp": FileTransferStrategyTypes.FTP,
    "globus": FileTransferStrategyTypes.GLOBUS,
}


class FtCallDepReturnValue(str, enum.Enum):
    TO = "to"
    FROM = "from"
    FROM_TO = "from_to"
