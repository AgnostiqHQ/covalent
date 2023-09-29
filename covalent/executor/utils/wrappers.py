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

"""
Helper functions for the local executor
"""

import io
import os
import traceback
from contextlib import redirect_stderr, redirect_stdout
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


class Signals(Enum):
    """
    Signals to enable communication between the executors and Covalent dispatcher
    """

    GET = 0
    PUT = 1
    EXIT = 2


def io_wrapper(
    fn: Callable,
    args: List,
    kwargs: Dict,
    workdir: str = ".",
) -> Tuple[Any, str, str, str]:
    """Wrapper function to execute the given function in a separate
    process and capture stdout and stderr"""
    with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
        try:
            Path(workdir).mkdir(parents=True, exist_ok=True)
            current_dir = os.getcwd()
            os.chdir(workdir)
            output = fn(*args, **kwargs)
            tb = ""
        except Exception as ex:
            output = None
            tb = "".join(traceback.TracebackException.from_exception(ex).format())
        finally:
            os.chdir(current_dir)
    return output, stdout.getvalue(), stderr.getvalue(), tb
