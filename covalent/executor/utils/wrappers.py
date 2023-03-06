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

"""
Helper functions for the local executor
"""

import io
import traceback
from contextlib import redirect_stderr, redirect_stdout
from enum import Enum
from typing import Any, Callable, Dict, List, Tuple


class Signals(Enum):
    """
    Signals to enable communication between the executors and Covalent dispatcher
    """

    GET = 0
    PUT = 1
    EXIT = 2


def io_wrapper(fn: Callable, args: List, kwargs: Dict) -> Tuple[Any, str, str, str]:
    """Wrapper function to execute the given function in a separate
    process and capture stdout and stderr"""
    with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
        try:
            output = fn(*args, **kwargs)
            tb = ""
        except Exception as ex:
            output = None
            tb = "".join(traceback.TracebackException.from_exception(ex).format())
    return output, stdout.getvalue(), stderr.getvalue(), tb
