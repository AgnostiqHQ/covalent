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

"""Unit tests for the importer entry point"""

import pytest

from covalent_dispatcher._core.data_modules.importer import import_derived_manifest


@pytest.mark.asyncio
async def test_import_derived_manifest(mocker):
    mock_import_manifest = mocker.patch(
        "covalent_dispatcher._core.data_modules.importer._import_manifest",
    )
    mock_handle_redispatch = mocker.patch(
        "covalent_dispatcher._core.data_modules.importer.handle_redispatch",
    )

    mock_manifest = {}
    await import_derived_manifest(mock_manifest, "parent_dispatch", True)

    mock_import_manifest.assert_called()
    mock_handle_redispatch.assert_called()
