from pathlib import Path
from unittest.mock import Mock

import pytest

from covalent._file_transfer.enums import FileSchemes, FileTransferStrategyTypes
from covalent._file_transfer.file import File


class TestFile:
    def test_raise_exception_invalid_args(self):
        # do not accept Path object as local filepath
        with pytest.raises(AttributeError):
            File(Path())
        # do not accept invalid scheme
        with pytest.raises(ValueError):
            File("myownprotocol://file.txt")

    def test_raise_exception_valid_args(self):
        # valid filepaths should not raise errors
        File("file:///home/one.csv")
        File(None)

    @pytest.mark.parametrize(
        "filepath, expected_scheme",
        [
            ("http://example.com/file", FileSchemes.HTTP),
            ("https://example.com/file", FileSchemes.HTTPS),
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
            ("/home/ubuntu/my_dir", "/home/ubuntu/my_dir"),
            ("/home/ubuntu/my_dir/", "/home/ubuntu/my_dir/"),
            ("/home/ubuntu/my_dir//", "/home/ubuntu/my_dir/"),
            ("/home/ubuntu/my_dir///", "/home/ubuntu/my_dir/"),
            ("/home/ubuntu/my_dir//../", "/home/ubuntu/"),
            ("file:///home/ubuntu/observations.csv", "/home/ubuntu/observations.csv"),
            ("file:/home/ubuntu/observations.csv", "/home/ubuntu/observations.csv"),
        ],
    )
    def test_get_filepath(self, filepath, expected_filepath):
        assert File.get_path_obj(filepath) == expected_filepath

    @pytest.mark.parametrize(
        "provided_uri, expected_uri",
        [
            ("/home/ubuntu/observations.csv", "file:///home/ubuntu/observations.csv"),
            ("file:/home/ubuntu/observations.csv", "file:///home/ubuntu/observations.csv"),
            ("file:///home/ubuntu/observations.csv", "file:///home/ubuntu/observations.csv"),
            ("https://example.com/my_route", "https://example.com/my_route"),
            ("http://example.com/my_route", "http://example.com/my_route"),
        ],
    )
    def test_get_uri(self, provided_uri, expected_uri):
        assert File(provided_uri).uri == expected_uri

    @pytest.mark.parametrize(
        "filepath, is_directory",
        [
            ("/home/ubuntu/observations.csv", False),
            ("/home/ubuntu/observations", False),
            ("/home/ubuntu/observations/", True),
        ],
    )
    def test_is_directory(self, filepath, is_directory):
        # check for trailing slash
        assert File(filepath).is_dir == is_directory
        # test is_dir override
        assert File(filepath, is_dir=True).is_dir

    def test_include_folder(self):
        MOCK_FILEPATH = "/home/ubuntu/my_dir"
        assert File(MOCK_FILEPATH).filepath == MOCK_FILEPATH
        # ensure trailing slash is removed when dir is to be included in file transfer
        # ensure trailing slash is added when dir is not to be included in file transfer (only contents) - default
        assert File(MOCK_FILEPATH, is_dir=True).filepath == f"{MOCK_FILEPATH}/"
        assert File(MOCK_FILEPATH, include_folder=True).filepath == MOCK_FILEPATH
        assert File(f"{MOCK_FILEPATH}/", include_folder=True).filepath == MOCK_FILEPATH
        assert File(f"{MOCK_FILEPATH}/", include_folder=False).filepath == f"{MOCK_FILEPATH}/"
        # this is not a dir so we do not add traling slash
        assert File(MOCK_FILEPATH, include_folder=False).filepath == MOCK_FILEPATH
