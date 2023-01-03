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

"""
Tests for the asset manager
"""

import os
import tempfile

from covalent_dispatcher._core.data_modules import asset_manager as am
from covalent_dispatcher._dal.asset import Asset


def test_upload_asset():

    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        src_path = temp.name
        src_key = os.path.basename(src_path)
    storage_path = "/tmp"
    a = Asset(storage_path, src_key)
    a.store_data("Hello\n")

    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        dest_path = temp.name
        dest_key = os.path.basename(dest_path)

    am._upload_asset(a, dest_path)
    #    a.upload(dest_path)

    with open(dest_path, "r") as f:
        assert f.read() == "Hello\n"
    os.unlink(dest_path)


def test_download_asset():

    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        src_path = temp.name
        src_key = os.path.basename(src_path)
    with open(src_path, "w") as f:
        f.write("Hello\n")

    storage_path = "/tmp"
    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        dest_path = temp.name
        dest_key = os.path.basename(dest_path)

    a = Asset(storage_path, dest_key)
    a.set_remote(src_path)

    am._download_asset(a)
    # a.download()

    assert a.load_data() == "Hello\n"

    os.unlink(dest_path)
