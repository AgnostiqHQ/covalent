from pathlib import Path

import pytest

from covalent._file_transfer.enums import FileSchemes
from covalent._file_transfer.file import File


class TestFile:
    """Test File object methods"""

    def test_raise_exception_invalid_args(self):
        # do not accept no provided local or remote path
        with pytest.raises(AttributeError):
            File(None)
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

    @pytest.mark.parametrize(
        "filepath, expected_filepath",
        [
            ("/home/ubuntu/observations.csv", "/home/ubuntu/observations.csv"),
            ("file:///home/ubuntu/observations.csv", "/home/ubuntu/observations.csv"),
            ("file:/home/ubuntu/observations.csv", "/home/ubuntu/observations.csv"),
        ],
    )
    def test_get_filepath(self, filepath, expected_filepath):
        assert File.get_file_path(filepath) == expected_filepath

    @pytest.mark.parametrize(
        "filepath, is_directory",
        [
            ("/home/ubuntu/observations.csv", False),
            ("/home/ubuntu/observations", False),
            ("/home/ubuntu/observations/", True),
        ],
    )
    def test_is_directory(self, filepath, is_directory):
        assert File(filepath).is_directory == is_directory
