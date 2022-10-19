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

"""Lattice functional test"""


from covalent_ui.api.v1.utils.file_handle import transportable_object, validate_data
from tests.covalent_ui_backend_tests.utils.assert_data.lattices import seed_lattice_data
from tests.covalent_ui_backend_tests.utils.client_template import TestClientTemplate

object_test_template = TestClientTemplate()
output_data = seed_lattice_data()


def test_transportable_object():
    obj_res = transportable_object(None)
    assert obj_res is None


def test_validate_unpickled_list():
    list_arr = ["Hello", " ", "World!"]
    obj_res = validate_data(list_arr)
    assert obj_res == "Hello World!"


def test_validate_unpickled_str():
    sample_str = "dispatch.get_result()"
    obj_res = validate_data(sample_str)
    assert obj_res == "dispatch.get_result()"
