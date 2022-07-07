from typing import Union

import pytest

from covalent._workflow.lepton import Lepton


def test_init_lepton():
    mock_lepton = Lepton(library_name="sample.so")

    # Test for base attributes of a Lepton
    assert mock_lepton.language == "python"
    assert mock_lepton.library_name == "sample.so"
    assert mock_lepton.function_name == ""
    assert mock_lepton.argtypes == []

    # Test supported languages
    supported_languages = ["C", "c", "python", "Python"]

    for language in supported_languages:
        assert language in mock_lepton._LANG_C or mock_lepton._LANG_PY

    # Check that unsupported languages appropriately raise a ValueError
    unsupported_languages = ["R", "haskell", "erlang"]

    for language in unsupported_languages:
        with pytest.raises(ValueError):
            Lepton(language=language)


def test_file_transfer_support():

    pass











def test_python_wrapper():
    pass


def test_c_wrapper():
    pass
