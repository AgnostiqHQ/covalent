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

"""
Server-side file transfer utilities
"""

from concurrent.futures import ThreadPoolExecutor

from covalent._file_transfer import FileTransfer
from covalent._shared_files import logger

app_log = logger.app_log
am_pool = ThreadPoolExecutor()


def cp(src_uri: str, dest_uri: str, transfer_options: dict = {}):
    ft = FileTransfer(src_uri, dest_uri)
    pre_hook, transfer_callable = FileTransfer(src_uri, dest_uri).cp()
    transfer_callable()
