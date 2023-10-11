# Copyright 2023 Agnostiq Inc.
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


from covalent.triggers import BaseTrigger, DatabaseTrigger, DirTrigger, SQLiteTrigger, TimeTrigger


class TriggerLoader:
    def __init__(self):
        self.available_triggers = {
            BaseTrigger.__name__: BaseTrigger,
            DatabaseTrigger.__name__: DatabaseTrigger,
            DirTrigger.__name__: DirTrigger,
            TimeTrigger.__name__: TimeTrigger,
            SQLiteTrigger.__name__: SQLiteTrigger,
        }

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __getitem__(self, key):
        return self.available_triggers.get(key)

    def __setitem__(self, key, value):
        self.available_triggers[key] = value


available_triggers = TriggerLoader()
