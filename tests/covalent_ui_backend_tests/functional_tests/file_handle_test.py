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

import shutil

from covalent_ui.api.v1.utils.file_handle import FileHandler, transportable_object, validate_data
from tests.covalent_ui_backend_tests.utils.assert_data.file_handle import mock_file_data
from tests.covalent_ui_backend_tests.utils.assert_data.lattices import seed_lattice_data
from tests.covalent_ui_backend_tests.utils.client_template import TestClientTemplate
from tests.covalent_ui_backend_tests.utils.main import log_output_data, seed_files

object_test_template = TestClientTemplate()
output_data = seed_lattice_data()
mock_data = mock_file_data()


def test_transportable_object():
    """Handle file objects / unpickled objects for transportable objects"""
    obj_res = transportable_object(None)
    assert obj_res is None


def test_validate_unpickled_list():
    """Handle file objects / unpickled objects for lists"""
    list_arr = ["Hello", " ", "World!"]
    obj_res = validate_data(list_arr)
    assert obj_res == "Hello World!"


def test_validate_unpickled_str():
    """Handle file objects / unpickled objects for literals"""
    sample_str = "dispatch.get_result()"
    obj_res = validate_data(sample_str)
    assert obj_res == "dispatch.get_result()"


def test_validate_unpickled_dict():
    """Handle file objects / unpickled objects for dict"""
    test_unpickled_dict = {"type": "electron"}
    obj_res = validate_data(test_unpickled_dict)
    assert obj_res == str(test_unpickled_dict)


def test_validate_none():
    """Handle file objects / unpickled objects for null objects"""
    obj_res = validate_data(None)
    assert obj_res == "None"


def test_read_from_text():
    seed_files()
    test_data = mock_data["test_read_text"]
    handler = FileHandler(test_data["file_path"])
    text_value = handler.read_from_text(test_data["case1"]["file_name"])
    assert text_value == test_data["case1"]["response_data"]
    shutil.rmtree(log_output_data["lattice_files"]["path"])


def test_read_from_text_exception():
    seed_files()
    test_data = mock_data["test_read_text"]
    handler = FileHandler(test_data["file_path"])
    text_value = handler.read_from_text(test_data["case2"]["file_name"])
    assert text_value == test_data["case2"]["response_data"]
    shutil.rmtree(log_output_data["lattice_files"]["path"])


def test_unpickle_data_exception():
    seed_files()
    test_data = mock_data["test_unpickle"]
    handler = FileHandler(test_data["file_path"])
    text_value = handler.read_from_pickle(test_data["case1"]["file_name"])
    assert text_value == test_data["case1"]["response_data"]
    shutil.rmtree(log_output_data["lattice_files"]["path"])
