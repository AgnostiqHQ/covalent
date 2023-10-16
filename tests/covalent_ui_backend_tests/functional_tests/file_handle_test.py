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

"""Lattice functional test"""

import shutil

from covalent_ui.api.v1.utils.file_handle import FileHandler, transportable_object, validate_data

from ..utils.assert_data.file_handle import mock_file_data
from ..utils.assert_data.lattices import seed_lattice_data
from ..utils.client_template import TestClientTemplate
from ..utils.trigger_events import log_output_data, seed_files

object_test_template = TestClientTemplate()
output_data = seed_lattice_data()
mock_data = mock_file_data()


def remove_mock_files():
    shutil.rmtree(log_output_data["lattice_files"]["path"])
    shutil.rmtree(log_output_data["log_files"]["path"])


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
    assert obj_res == test_unpickled_dict


def test_validate_none():
    """Handle file objects / unpickled objects for null objects"""
    obj_res = validate_data(None)
    assert obj_res == (None, None)


def test_read_from_text():
    """Test read from text"""
    seed_files()
    test_data = mock_data["test_read_text"]
    handler = FileHandler(test_data["file_path"])
    text_value = handler.read_from_text(test_data["case1"]["file_name"])
    assert text_value == test_data["case1"]["response_data"]
    remove_mock_files()


def test_read_from_text_exception():
    """Test read from text with exceptions"""
    seed_files()
    test_data = mock_data["test_read_text"]
    handler = FileHandler(test_data["file_path"])
    text_value = handler.read_from_text(test_data["case2"]["file_name"])
    assert text_value == test_data["case2"]["response_data"]
    remove_mock_files()


def test_unpickle_data_exception():
    """Test unpickling data with exceptions"""
    seed_files()
    test_data = mock_data["test_unpickle"]
    handler = FileHandler(test_data["file_path"])
    text_value = handler.read_from_pickle(test_data["case1"]["file_name"])
    assert text_value == test_data["case1"]["response_data"]
    remove_mock_files()


def test_models_helper():
    from covalent_ui.api.v1.utils.models_helper import SortBy

    assert (SortBy._missing_("runtime")) is not None
