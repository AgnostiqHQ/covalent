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

"""Tests for Asset"""

import os
import tempfile

from covalent_dispatcher._dal.asset import Asset


def test_asset_load_data():
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as temp:
        temp.write("Hello\n")
        temppath = temp.name
        key = os.path.basename(temppath)

    storage_path = "/tmp"
    a = Asset(storage_path, key)
    assert a.load_data() == "Hello\n"
    os.unlink(temppath)


def test_asset_store_data():
    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        temppath = temp.name
        key = os.path.basename(temppath)
    storage_path = "/tmp"
    a = Asset(storage_path, key)
    a.store_data("Hello\n")

    with open(temppath, "r") as f:
        assert f.read() == "Hello\n"

    os.unlink(temppath)
