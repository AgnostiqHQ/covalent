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


class MissingLatticeRecordError(Exception):
    pass


class TaskRuntimeError(Exception):
    pass


class TaskCancelledError(Exception):
    pass


class CommandNotFoundError(Exception):
    pass


class ConfigLockError(Exception):
    """Raised when the lock on the Covalent configuration file cannot be acquired.

    Attributes:
        lock_file: Path of the lock file which could not be acquired.
    """

    def __init__(self, lock_file: str) -> None:
        self.lock_file = lock_file
        super().__init__(
            f"Unable to acquire a lock on the Covalent configuration file '{lock_file}'. "
            "Either another Covalent process is holding the lock, or the filesystem "
            "hosting the configuration directory does not support file locking. Set the "
            "COVALENT_CONFIG_DIR environment variable to a directory on a filesystem "
            "which supports file locking, such as a local disk."
        )
