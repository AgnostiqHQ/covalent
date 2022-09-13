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

"""Workflow stack testing of File Transfer operations."""

from pathlib import Path
from unittest.mock import Mock

import pytest

import covalent as ct
import covalent._results_manager.results_manager as rm
from covalent._file_transfer.enums import Order


@pytest.mark.parametrize(
    "is_before",
    [(True), (False)],
)
def test_local_file_transfer(tmp_path: Path, is_before):
    """
    Test to check if electron is able to transfer file from source to destination path
    """

    order = Order.BEFORE if is_before else Order.AFTER
    MOCK_CONTENTS = "hello"

    source_file = tmp_path / Path("source.txt")
    dest_file = tmp_path / Path("dest.txt")

    source_file.write_text(MOCK_CONTENTS)

    @ct.electron(files=[ct.fs.FileTransfer(str(source_file), str(dest_file), order=order)])
    def test_transfer_me(files=[]):
        pass

    @ct.lattice
    def workflow():
        return test_transfer_me()

    dispatch_id = ct.dispatch(workflow)()

    workflow_result = rm.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)

    assert dest_file.read_text() == MOCK_CONTENTS

    dest_file.unlink()
    source_file.unlink()


def test_local_file_transfer_with_kwargs_single(tmp_path: Path):
    """
    Test to check if electron is able to transfer file from source to destination path and
    includes injected 'files' kwarg
    """

    MOCK_CONTENTS = "hello"

    source_file = tmp_path / Path("source.txt")
    dest_file = tmp_path / Path("dest.txt")

    source_file.write_text(MOCK_CONTENTS)

    ft = ct.fs.FileTransfer(str(source_file), str(dest_file))

    @ct.electron(files=[ft])
    def test_transfer(files=[]):
        return files

    @ct.lattice
    def workflow():
        return test_transfer()

    dispatch_id = ct.dispatch(workflow)()

    workflow_result = rm.get_result(dispatch_id, wait=True)
    rm._delete_result(dispatch_id)

    assert len(workflow_result.result) == 1
    assert workflow_result.result == [(ft.from_file.filepath, ft.to_file.filepath)]

    dest_file.unlink()
    source_file.unlink()


def test_local_file_transfer_with_kwargs_multiple(tmp_path: Path):
    """
    Test to check if electron is able to transfer file from source to destination path and
    includes injected 'files' kwargs
    """

    MOCK_CONTENTS = "hello"

    source_file_1 = tmp_path / Path("source.txt")
    dest_file_1 = tmp_path / Path("dest.txt")

    source_file_2 = tmp_path / Path("source2.txt")
    dest_file_2 = tmp_path / Path("dest2.txt")

    source_file_1.write_text(MOCK_CONTENTS)
    source_file_2.write_text(MOCK_CONTENTS)

    ft1 = ct.fs.FileTransfer(str(source_file_1), str(dest_file_1))
    ft2 = ct.fs.FileTransfer(str(source_file_2), str(dest_file_2))

    @ct.electron(files=[ft1, ft2])
    def test_transfer(files=[]):
        return files

    @ct.lattice
    def workflow():
        return test_transfer()

    dispatch_id = ct.dispatch(workflow)()

    workflow_result = rm.get_result(dispatch_id, wait=True)
    rm._delete_result(dispatch_id)

    assert len(workflow_result.result) == 2
    assert workflow_result.result == [
        (ft1.from_file.filepath, ft1.to_file.filepath),
        (ft2.from_file.filepath, ft2.to_file.filepath),
    ]

    for f in [source_file_1, dest_file_1, source_file_2, dest_file_2]:
        f.unlink()


def test_local_file_transfer_collected_nodes(tmp_path: Path):
    """
    Test to check if electron with iterable outputs works with file transfers.
    """
    MOCK_CONTENTS = "hello"

    source_file_1 = tmp_path / Path("source.txt")
    dest_file_1 = tmp_path / Path("dest.txt")

    source_file_2 = tmp_path / Path("source2.txt")
    dest_file_2 = tmp_path / Path("dest2.txt")

    source_file_1.write_text(MOCK_CONTENTS)
    source_file_2.write_text(MOCK_CONTENTS)

    ft1 = ct.fs.FileTransfer(str(source_file_1), str(dest_file_1))
    ft2 = ct.fs.FileTransfer(str(source_file_2), str(dest_file_2))

    @ct.electron(files=[ft1, ft2])
    def test_transfer(files=[]):
        _, f_1 = files[0]
        _, f_2 = files[1]
        with open(f_1, "r") as f:
            content_1 = f.readlines()[0]
        with open(f_2, "r") as f:
            content_2 = f.readlines()[0]
        return content_1, content_2

    @ct.lattice
    def workflow():
        a, b = test_transfer()
        return a, b

    dispatch_id = ct.dispatch(workflow)()

    workflow_result = rm.get_result(dispatch_id, wait=True)
    rm._delete_result(dispatch_id)

    assert len(workflow_result.result) == 2
    assert workflow_result.result == (MOCK_CONTENTS, MOCK_CONTENTS)
    for f in [source_file_1, dest_file_1, source_file_2, dest_file_2]:
        f.unlink()


def test_local_file_transfer_transfer_from(tmp_path: Path, mocker):
    """
    Test to check if electron is able to transfer file from source to destination path and
    includes injected 'files' kwarg
    """

    MOCK_CONTENTS = "hello"

    source_file = tmp_path / Path("source.txt")
    source_file.write_text(MOCK_CONTENTS)

    # mock Popen so ssh rsync command does not run
    Popen = Mock()
    Popen.communicate.return_value = ("", "")
    Popen.returncode = 0
    mocker.patch("covalent._file_transfer.strategies.rsync_strategy.Popen", return_value=Popen)

    ft = ct.fs.TransferFromRemote(str(source_file))

    @ct.electron(files=[ft])
    def test_transfer(files=[]):
        return files  # first element should be 'destination' / 'to' filepath

    @ct.lattice
    def workflow():
        return test_transfer()

    dispatch_id = ct.dispatch(workflow)()

    workflow_result = rm.get_result(dispatch_id, wait=True)
    rm._delete_result(dispatch_id)

    assert workflow_result.result == [(ft.from_file.filepath, ft.to_file.filepath)]

    source_file.unlink()


def test_local_file_transfer_transfer_to(tmp_path: Path, mocker):
    """
    Test to check if electron is able to transfer file to destination from source (temp) path and
    includes injected 'files' kwarg
    """

    MOCK_CONTENTS = "hello"

    dest_file = tmp_path / Path("dest.txt")
    dest_file.write_text(MOCK_CONTENTS)

    # mock Popen so ssh rsync command does not run
    Popen = Mock()
    Popen.communicate.return_value = ("", "")
    Popen.returncode = 0
    mocker.patch("covalent._file_transfer.strategies.rsync_strategy.Popen", return_value=Popen)

    ft = ct.fs.TransferToRemote(str(dest_file))

    @ct.electron(files=[ft])
    def test_transfer(files=[]):
        return files  # first element should be 'source' / 'from' filepath

    @ct.lattice
    def workflow():
        return test_transfer()

    dispatch_id = ct.dispatch(workflow)()

    workflow_result = rm.get_result(dispatch_id, wait=True)
    rm._delete_result(dispatch_id)

    assert workflow_result.result == [(ft.from_file.filepath, ft.to_file.filepath)]

    dest_file.unlink()
