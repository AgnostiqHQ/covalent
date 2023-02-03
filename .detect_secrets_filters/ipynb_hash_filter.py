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

"""Filters for `detect-secrets` pre-commit hook."""

import json
import re
from functools import lru_cache
from typing import Pattern

from detect_secrets.core.plugins.util import Plugin


def is_pynb_hash(filename: str, plugin: Plugin, secret: str) -> bool:
    """
    A filter to make sure that we skip the interpreter hash.

    Args:
        filename: The name of the file on which detect-secrets is running.
        plugin: The plugin which found the secret.
        secret: The string which is marked as a secret.

    Returns:
        bool: True to skip the secret, and False to not skip it.

    """
    plugin_json = plugin.json()
    if filename.endswith(".ipynb") and plugin_json["name"] == "HexHighEntropyString":
        with open(filename, encoding="utf-8") as pynb_file:
            json_obj = json.load(pynb_file)
            metadata = json_obj.get("metadata")
            if not metadata:
                return False
            interpreter = metadata.get("interpreter")
            if not interpreter:
                return False
            hash_ipynb = interpreter.get("hash")
            if hash_ipynb == secret:
                return True
    return False


def is_pynb_image(filename: str, plugin: Plugin, secret: str, line: str) -> bool:
    """
    A filter to make sure that we skip the utf-8 representation of png images.

    Args:
        filename: The name of the file on which detect-secrets is running.
        plugin: The plugin which found the secret.
        secret: The string which is marked as a secret.
        line: The line on which the secret was found.

    Returns:
        bool: True to skip the secret, and False to not skip it.

    """
    plugin_json = plugin.json()
    if filename.endswith(".ipynb") and plugin_json["name"] == "Base64HighEntropyString":
        return bool(_get_img_regex().search(line))
    return False


@lru_cache(maxsize=1)
def _get_img_regex() -> Pattern:
    """
    In order to get the cached regex to be used for finding the string
    representation of images.
    https://github.com/Yelp/detect-secrets/blob/master/docs/filters.md#1-cache-when-possible

    Returns:
        pattern: A Pattern object gotten after compiling the regex.
    """
    return re.compile(
        r'"image/png": ".*",',
        re.IGNORECASE,
    )
