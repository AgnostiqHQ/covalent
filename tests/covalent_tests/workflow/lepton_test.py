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

"""Unit tests for leptons."""

import inspect

import pytest

from covalent._workflow.electron import Electron
from covalent._workflow.lepton import Lepton


def test_lepton_init(mocker, monkeypatch):
    monkeypatch.setattr(
        "covalent._shared_files.defaults._DEFAULT_CONSTRAINT_VALUES", {"executor": "local"}
    )
    init_mock = mocker.patch("covalent._workflow.lepton.Electron.__init__", return_value=None)
    set_metadata_mock = mocker.patch(
        "covalent._workflow.lepton.Electron.set_metadata", return_value=None
    )
    wrap_mock = mocker.patch(
        "covalent._workflow.lepton.Lepton.wrap_task", return_value="wrapper function"
    )

    lepton = Lepton(
        language="lang",
        library_name="libname",
        function_name="funcname",
        argtypes=[(int, "type")],
    )

    init_mock.assert_called_once_with("wrapper function")
    wrap_mock.assert_called_once_with()
    set_metadata_mock.assert_called_once_with("executor", "local")

    assert lepton.language == "lang"
    assert lepton.library_name == "libname"
    assert lepton.function_name == "funcname"
    assert lepton.argtypes == [("int", "type")]

    assert isinstance(lepton, Electron)


def test_lepton_attributes():
    def filter_attributes(attributes):
        return [a for a in attributes if not (a[0].startswith("__") and a[0].endswith("__"))]

    electron_attributes = filter_attributes(inspect.getmembers(Electron))
    lepton_attributes = filter_attributes(inspect.getmembers(Lepton))

    expected_attributes = [
        ("INPUT", 0),
        ("OUTPUT", 1),
        ("INPUT_OUTPUT", 2),
        ("_LANG_PY", ["Python", "python"]),
        ("_LANG_C", ["C", "c"]),
        ("wrap_task", Lepton.wrap_task),
    ]

    assert sorted(electron_attributes + expected_attributes) == sorted(lepton_attributes)


@pytest.mark.parametrize("language", ["python", "C"])
def test_wrap_task(mocker, language):
    pass
