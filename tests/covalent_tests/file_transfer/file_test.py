from pathlib import Path
from unittest.mock import Mock

import pytest

from covalent._file_transfer.enums import FileSchemes, FileTransferStrategyTypes
from covalent._file_transfer.file import File


class TestFile:
    """Test File object methods"""

    def test_raise_exception_invalid_args(self):
        # do not accept Path object as local filepath
        with pytest.raises(AttributeError):
            File(Path())
        # do not accept invalid scheme
        with pytest.raises(ValueError):
            File("myownprotocol://file.txt")

    @pytest.mark.parametrize(
        "filepath, expected_scheme",
        [
            ("/home/ubuntu/observations.csv", FileSchemes.File),
            ("file:/home/ubuntu/observations.csv", FileSchemes.File),
            ("file:///home/ubuntu/observations.csv", FileSchemes.File),
            ("s3://mybucket/observations.csv", FileSchemes.S3),
            ("globus://037f054a-15cf-11e8-b611-0ac6873fc731/observations.txt", FileSchemes.Globus),
        ],
    )
    def test_scheme_resolution(self, filepath, expected_scheme):
        assert File(filepath).scheme == expected_scheme

    def test_scheme_to_strategy_map(self):
        assert File("s3://file").mapped_strategy_type == FileTransferStrategyTypes.S3
        assert File("ftp://file").mapped_strategy_type == FileTransferStrategyTypes.FTP
        assert File("globus://file").mapped_strategy_type == FileTransferStrategyTypes.GLOBUS
        assert File("file://file").mapped_strategy_type == FileTransferStrategyTypes.Rsync
        assert File("https://example.com").mapped_strategy_type == FileTransferStrategyTypes.HTTP
        assert File("http://example.com").mapped_strategy_type == FileTransferStrategyTypes.HTTP

    def test_is_remote_flag(self):
        assert File("s3://file").is_remote
        assert File("ftp://file").is_remote
        assert File("globus://file").is_remote
        assert File("file://file").is_remote is False
        assert File("file://file", is_remote=True).is_remote
        assert File("https://example.com").is_remote
        assert File("http://example.com").is_remote

    @pytest.mark.parametrize(
        "filepath, expected_filepath",
        [
            ("/home/ubuntu/observations.csv", "/home/ubuntu/observations.csv"),
            ("file:///home/ubuntu/observations.csv", "/home/ubuntu/observations.csv"),
            ("file:/home/ubuntu/observations.csv", "/home/ubuntu/observations.csv"),
        ],
    )
    def test_get_filepath(self, filepath, expected_filepath):
        assert File.get_filepath(filepath) == expected_filepath

    @pytest.mark.parametrize(
        "filepath, is_directory",
        [
            ("/home/ubuntu/observations.csv", False),
            ("/home/ubuntu/observations", False),
            ("/home/ubuntu/observations/", True),
        ],
    )
    def test_is_directory(self, filepath, is_directory):
        assert File.is_directory(filepath) == is_directory
