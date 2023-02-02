# Copyright 2023 Agnostiq Inc.
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

from pathlib import Path

from .base import BaseTrigger
from .dir_trigger import DirTrigger


class TriggerLoader:
    def __init__(self):
        self.available_triggers = {
            BaseTrigger.__name__: BaseTrigger,
            DirTrigger.__name__: DirTrigger,
        }

        self.load_user_triggers()

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(TriggerLoader, cls).__new__(cls)
        return cls.instance

    def __getitem__(self, key):
        return self.available_triggers.get(key)

    def __setitem__(self, key, value):
        self.available_triggers[key] = value

    def load_user_triggers(self):
        user_triggers_path = Path("~/.covalent/triggers/")
        if user_triggers_path.exists():
            # TODO: Load user triggers to available triggers here
            pass


available_triggers = TriggerLoader()
