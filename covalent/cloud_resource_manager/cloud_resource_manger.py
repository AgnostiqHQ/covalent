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

from typing import Optional


class CloudResourceManager:
    def __init__(
        self, executor_name: str, tf_var_1: Optional[str] = None, tf_var_2: Optional[str] = None
    ):
        self.executor_name = executor_name
        self.tf_var_1 = tf_var_1
        self.tf_var_2 = tf_var_2

    def get_terrafrom_filepath(self):
        """Get terraform file path. This will get the terraform filepath corresponding to the executor name."""
        return "terraform_filepath"

    def up(self):
        """Setup resources."""
        return "Resources are being setup."

    def down(self):
        """Teardown resources."""
        return "Resources are being torn down."

    def status(self):
        """Check status of resources."""
        return "Resources are in a good state."


# TODO - Singleton or not?
crm = CloudResourceManager()
