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
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Callable, Dict, List, Tuple

import cloudpickle as pickle

from covalent._workflow.depsbash import DepsBash
from covalent._workflow.depscall import RESERVED_RETVAL_KEY__FILES, DepsCall
from covalent._workflow.depspip import DepsPip
from covalent._workflow.transport import TransportableObject


def wrapper_fn(
    function: TransportableObject,
    call_before: List[Tuple[TransportableObject, TransportableObject, TransportableObject]],
    call_after: List[Tuple[TransportableObject, TransportableObject, TransportableObject]],
    *args,
    **kwargs,
):
    """Wrapper for serialized callable.

    Execute preparatory shell commands before deserializing and
    running the callable. This is the actual function to be sent to
    the various executors.

    """

    cb_retvals = {}
    for tup in call_before:
        serialized_fn, serialized_args, serialized_kwargs, retval_key = tup
        cb_fn = serialized_fn.get_deserialized()
        cb_args = serialized_args.get_deserialized()
        cb_kwargs = serialized_kwargs.get_deserialized()
        retval = cb_fn(*cb_args, **cb_kwargs)

        # we always store cb_kwargs dict values as arrays to factor in non-unique values
        if retval_key and retval_key in cb_retvals:
            cb_retvals[retval_key].append(retval)
        elif retval_key:
            cb_retvals[retval_key] = [retval]

    # if cb_retvals key only contains one item this means it is a unique (non-repeated) retval key
    # so we only return the first element however if it is a 'files' kwarg we always return as a list
    cb_retvals = {
        key: value[0] if len(value) == 1 and key != RESERVED_RETVAL_KEY__FILES else value
        for key, value in cb_retvals.items()
    }

    fn = function.get_deserialized()

    new_args = [arg.get_deserialized() for arg in args]

    new_kwargs = {k: v.get_deserialized() for k, v in kwargs.items()}

    # Inject return values into kwargs
    for key, val in cb_retvals.items():
        new_kwargs[key] = val

    output = fn(*new_args, **new_kwargs)

    for tup in call_after:
        serialized_fn, serialized_args, serialized_kwargs, retval_key = tup
        ca_fn = serialized_fn.get_deserialized()
        ca_args = serialized_args.get_deserialized()
        ca_kwargs = serialized_kwargs.get_deserialized()
        ca_fn(*ca_args, **ca_kwargs)

    return TransportableObject(output)


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


# Copied from runner.py
def _gather_deps(deps, call_before_objs_json, call_after_objs_json) -> Tuple[List, List]:
    """Assemble deps for a node into the final call_before and call_after"""

    call_before = []
    call_after = []

    # Rehydrate deps from JSON
    if "bash" in deps:
        dep = DepsBash()
        dep.from_dict(deps["bash"])
        call_before.append(dep.apply())

    if "pip" in deps:
        dep = DepsPip()
        dep.from_dict(deps["pip"])
        call_before.append(dep.apply())

    for dep_json in call_before_objs_json:
        dep = DepsCall()
        dep.from_dict(dep_json)
        call_before.append(dep.apply())

    for dep_json in call_after_objs_json:
        dep = DepsCall()
        dep.from_dict(dep_json)
        call_after.append(dep.apply())

    return call_before, call_after


# URIs are just file paths
def run_task_from_uris(
    function_uri: str,
    deps_uri: str,
    call_before_uri: str,
    call_after_uri: str,
    args_uris: str,
    kwargs_uris: str,
    output_uri: str,
    stdout_uri: str,
    stderr_uri: str,
):

    prefix = "file://"
    prefix_len = len(prefix)

    with open(stdout_uri, "w") as stdout, open(stderr_uri, "w") as stderr:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                if function_uri.startswith(prefix):
                    function_uri = function_uri[prefix_len:]

                with open(function_uri, "rb") as f:
                    serialized_fn = pickle.load(f)

                ser_args = []
                ser_kwargs = {}
                for uri in args_uris:
                    if uri.startswith(prefix):
                        uri = uri[prefix_len:]
                    with open(uri, "rb") as f:
                        ser_args.append(pickle.load(f))

                for key, uri in kwargs_uris.items():
                    if uri.startswith(prefix):
                        uri = uri[prefix_len:]
                    with open(uri, "rb") as f:
                        ser_kwargs[key] = pickle.load(f)

                if deps_uri.startswith(prefix):
                    deps_uri = deps_uri[prefix_len:]
                with open(deps_uri, "rb") as f:
                    deps_json = pickle.load(f)

                if call_before_uri.startswith(prefix):
                    call_before_uri = call_before_uri[prefix_len:]
                with open(call_before_uri, "rb") as f:
                    call_before_json = pickle.load(f)

                if call_after_uri.startswith(prefix):
                    call_after_uri = call_after_uri[prefix_len:]
                with open(call_after_uri, "rb") as f:
                    call_after_json = pickle.load(f)

                call_before, call_after = _gather_deps(
                    deps_json, call_before_json, call_after_json
                )

                exception_occurred = False

                ser_output = wrapper_fn(
                    serialized_fn, call_before, call_after, *ser_args, **ser_kwargs
                )

                with open(output_uri, "wb") as f:
                    pickle.dump(ser_output, f)

            except Exception as ex:
                exception_occurred = True
                tb = "".join(traceback.TracebackException.from_exception(ex).format())
                print(tb, file=sys.stderr)
                output_uri = None

    return output_uri, stdout_uri, stderr_uri, exception_occurred
