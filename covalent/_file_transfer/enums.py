# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

import enum


class Order(str, enum.Enum):
    BEFORE = "before"
    AFTER = "after"


class FileSchemes(str, enum.Enum):
    File = "file"
    S3 = "s3"
    Globus = "globus"
    HTTP = "http"
    HTTPS = "https"
    FTP = "ftp"


class FileTransferStrategyTypes(str, enum.Enum):
    Rsync = "rsync"
    HTTP = "http"
    S3 = "s3"
    FTP = "ftp"
    GLOBUS = "globus"


SchemeToStrategyMap = {
    "file": FileTransferStrategyTypes.Rsync,
    "http": FileTransferStrategyTypes.HTTP,
    "https": FileTransferStrategyTypes.HTTP,
    "s3": FileTransferStrategyTypes.S3,
    "ftp": FileTransferStrategyTypes.FTP,
    "globus": FileTransferStrategyTypes.GLOBUS,
}


class FtCallDepReturnValue(str, enum.Enum):
    TO = "to"
    FROM = "from"
    FROM_TO = "from_to"
