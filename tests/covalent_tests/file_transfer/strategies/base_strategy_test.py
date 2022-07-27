from pathlib import Path
from unittest.mock import Mock, call

import pytest

from covalent._file_transfer import File
from covalent._file_transfer.file_transfer import FileTransfer
from covalent._file_transfer.strategies.rsync_strategy import Rsync
from covalent._file_transfer.strategies.transfer_strategy_base import FileTransferStrategy


class TestBaseFileTransferStrategy:
    @pytest.mark.parametrize(
        "is_from_temp, is_to_temp",
        [(True, True), (True, False), (False, False), (False, True)],
    )
    def test_pre_transfer_hook(self, mocker, is_from_temp, is_to_temp):
        strategy = Rsync()

        from_file = File() if is_from_temp else "/home/users.from.dat"
        to_file = File() if is_to_temp else "/home/users.to.dat"
        ft = FileTransfer(from_file, to_file, strategy=strategy)
        pre_transfer_hook_callable, file_transfer_callable = ft.cp()
        path_mock: Mock = mocker.patch(
            "covalent._file_transfer.strategies.transfer_strategy_base.Path"
        )
        pre_transfer_hook_callable()
        if is_from_temp:
            path_mock.assert_any_call(ft.from_file.filepath)
        if is_to_temp:
            path_mock.assert_any_call(ft.to_file.filepath)

        if is_from_temp and is_to_temp:
            assert path_mock().touch.call_count == 2
            assert path_mock().mkdir.call_count == 2
        elif is_from_temp or is_to_temp:
            assert path_mock().touch.call_count == 1
            assert path_mock().mkdir.call_count == 1
