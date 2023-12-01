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

import os
import requests 

from .. import File
from .transfer_strategy_base import FileTransferStrategy
from ..._shared_files import logger

app_log = logger.app_log


class HTTP(FileTransferStrategy):
    """
    Implements Base FileTransferStrategy class to use download files from public http(s) URLs.
    """

    # return callable to download here implies 'from' is a remote source
    def download(self, from_file: File, to_file: File = File()) -> File:
        from_filepath = from_file.uri
        to_filepath = to_file.filepath

        def callable():
            resp = requests.get(from_filepath, stream=True)
            resp.raise_for_status()
            with open(to_filepath, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    f.write(chunk)            

        return callable

    # Upload a file to a (possibly presigned) HTTP(s) URL
    def upload(self, from_file: File, to_file: File = File()) -> File:
        from_filepath = from_file.filepath
        to_filepath = to_file.uri
        filesize = os.path.getsize(from_filepath)

        def callable():
            with open(from_filepath, "rb") as reader:        
                # Workaround for Requests bug when streaming from empty files
                app_log.debug(f"uploading to {to_filepath}")                
                data = reader.read() if filesize < 50 else reader
                r = requests.put(to_filepath, headers={"Content-Length": str(filesize)}, data=data)
                r.raise_for_status()
                
        return callable        

    # HTTP Strategy does not support server-side copy between two remote URLs
    def cp(self, from_file: File, to_file: File = File()) -> File:
        raise NotImplementedError
