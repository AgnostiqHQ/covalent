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
import json
import os
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import requests

from covalent._shared_files.utils import get_qelectron_db_path
from covalent._workflow.depsbash import DepsBash
from covalent._workflow.depscall import RESERVED_RETVAL_KEY__FILES, DepsCall
from covalent._workflow.depspip import DepsPip
from covalent._workflow.transport import TransportableObject
from covalent.executor.utils import set_context
from covalent.executor.utils.serialize import deserialize_node_asset, serialize_node_asset


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


# Basic wrapper for executing a topologically sorted sequence of
# tasks. For the `task_specs` and `resources` schema see the comments
# for `AsyncBaseExecutor.send()`.


def run_task_group(
    task_specs: List[Dict],
    output_uris: List[Tuple[str, str, str]],
    results_dir: str,
    task_group_metadata: dict,
    server_url: str,
):
    """
    Run a task group.

    This is appropriate for executors which can access the Covalent
    server url directly. Exampl: LocalExecutor.

    """

    prefix = "file://"
    prefix_len = len(prefix)

    outputs = {}
    results = []
    dispatch_id = task_group_metadata["dispatch_id"]
    task_ids = task_group_metadata["node_ids"]
    gid = task_group_metadata["task_group_id"]

    os.environ["COVALENT_DISPATCH_ID"] = dispatch_id
    os.environ["COVALENT_DISPATCHER_URL"] = server_url

    for i, task in enumerate(task_specs):
        result_uri, stdout_uri, stderr_uri, qelectron_db_uri = output_uris[i]

        # Setting these to empty bytes in case the task fails
        qelectron_db_bytes = bytes()

        with open(stdout_uri, "w") as stdout, open(stderr_uri, "w") as stderr:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                try:
                    task_id = task["function_id"]
                    args_ids = task["args_ids"]
                    kwargs_ids = task["kwargs_ids"]

                    function_uri = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/{task_id}/assets/function"

                    # Download function
                    resp = requests.get(function_uri, stream=True)
                    resp.raise_for_status()
                    serialized_fn = deserialize_node_asset(resp.content, "function")

                    ser_args = []
                    ser_kwargs = {}

                    # Download args and kwargs
                    for node_id in args_ids:
                        url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/assets/output"
                        resp = requests.get(url, stream=True)
                        resp.raise_for_status()
                        ser_args.append(deserialize_node_asset(resp.content, "output"))

                    for k, node_id in kwargs_ids.items():
                        url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/assets/output"
                        resp = requests.get(url, stream=True)
                        resp.raise_for_status()
                        ser_kwargs[k] = deserialize_node_asset(resp.content, "output")

                    # Download deps, call_before, and call_after
                    hooks_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/{task_id}/assets/hooks"
                    resp = requests.get(hooks_url, stream=True)
                    resp.raise_for_status()
                    hooks_json = deserialize_node_asset(resp.content, "hooks")
                    deps_json = hooks_json.get("deps", {})
                    call_before_json = hooks_json.get("call_before", [])
                    call_after_json = hooks_json.get("call_after", [])

                    # Assemble and run the task
                    call_before, call_after = _gather_deps(
                        deps_json, call_before_json, call_after_json
                    )
                    exception_occurred = False

                    with set_context(dispatch_id, task_id):
                        transportable_output = wrapper_fn(
                            serialized_fn, call_before, call_after, *ser_args, **ser_kwargs
                        )

                    ser_output = serialize_node_asset(transportable_output, "output")
                    with open(result_uri, "wb") as f:
                        f.write(ser_output)

                    qelectron_db_path = get_qelectron_db_path(dispatch_id, task_id)
                    if qelectron_db_path is not None:
                        with open(qelectron_db_path / "data.mdb", "rb") as f:
                            qelectron_db_bytes = f.read()

                    outputs[task_id] = result_uri

                    result_summary = {
                        "node_id": task_id,
                        "output_uri": result_uri,
                        "stdout_uri": stdout_uri,
                        "stderr_uri": stderr_uri,
                        "qelectron_db_uri": qelectron_db_uri,
                        "exception_occurred": exception_occurred,
                    }

                except Exception as ex:
                    exception_occurred = True
                    tb = "".join(traceback.TracebackException.from_exception(ex).format())
                    print(tb, file=sys.stderr)
                    result_uri = None
                    result_summary = {
                        "node_id": task_id,
                        "output_uri": result_uri,
                        "stdout_uri": stdout_uri,
                        "stderr_uri": stderr_uri,
                        "qelectron_db_uri": qelectron_db_uri,
                        "exception_occurred": exception_occurred,
                    }

                    break

                finally:
                    # POST task artifacts
                    if result_uri:
                        upload_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/{task_id}/assets/output"
                        with open(result_uri, "rb") as f:
                            requests.put(upload_url, data=f)

                    sys.stdout.flush()
                    if stdout_uri:
                        upload_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/{task_id}/assets/stdout"
                        with open(stdout_uri, "rb") as f:
                            headers = {"Content-Length": os.path.getsize(stdout_uri)}
                            requests.put(upload_url, data=f)

                    sys.stderr.flush()
                    if stderr_uri:
                        upload_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/{task_id}/assets/stderr"
                        with open(stderr_uri, "rb") as f:
                            headers = {"Content-Length": os.path.getsize(stderr_uri)}
                            requests.put(upload_url, data=f)

                    if qelectron_db_bytes:
                        upload_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/{task_id}/assets/qelectron_db"
                        requests.put(upload_url, data=qelectron_db_bytes)

                    result_path = os.path.join(results_dir, f"result-{dispatch_id}:{task_id}.json")

                    with open(result_path, "w") as f:
                        json.dump(result_summary, f)

                    results.append(result_summary)

                    # Notify Covalent that the task has terminated
                    terminal_status = "FAILED" if exception_occurred else "COMPLETED"
                    url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/{task_id}/job"
                    data = {"status": terminal_status}
                    requests.put(url, json=data)

    # Deal with any tasks that did not run
    n = len(results)
    if n < len(task_ids):
        for i in range(n, len(task_ids)):
            result_summary = {
                "node_id": task_ids[i],
                "output_uri": "",
                "stdout_uri": "",
                "stderr_uri": "",
                "qelectron_db_uri": "",
                "exception_occurred": True,
            }

            results.append(result_summary)

            result_path = os.path.join(results_dir, f"result-{dispatch_id}:{task_id}.json")

            with open(result_path, "w") as f:
                json.dump(result_summary, f)

            url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/{task_id}/job"
            requests.put(url)


def run_task_group_alt(
    task_specs: List[Dict],
    resources: dict,
    output_uris: List[Tuple[str, str, str]],
    results_dir: str,
    task_group_metadata: dict,
    server_url: str,
):
    """
    Alternate form of run_task_group.

    This is appropriate for backends that cannot reach the Covalent
    server. Covalent will push input assets to the executor's
    persistent storage before invoking `Executor.send()` and pull output
    artifacts after `Executor.receive()`.

    Example: DaskExecutor.

    """

    prefix = "file://"
    prefix_len = len(prefix)

    outputs = {}
    results = []
    dispatch_id = task_group_metadata["dispatch_id"]
    task_ids = task_group_metadata["node_ids"]
    gid = task_group_metadata["task_group_id"]

    os.environ["COVALENT_STAGING_URI_PREFIX"] = f"file://{results_dir}/staging"
    os.environ["COVALENT_DISPATCH_ID"] = dispatch_id

    for i, task in enumerate(task_specs):
        result_uri, stdout_uri, stderr_uri, qelectron_db_uri = output_uris[i]

        # Setting these to empty bytes in case the task fails
        qelectron_db_bytes = bytes()

        with open(stdout_uri, "w") as stdout, open(stderr_uri, "w") as stderr:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                try:
                    task_id = task["function_id"]
                    args_ids = task["args_ids"]
                    kwargs_ids = task["kwargs_ids"]

                    # Load function
                    function_uri = resources["functions"][task_id]
                    if function_uri.startswith(prefix):
                        function_uri = function_uri[prefix_len:]

                    with open(function_uri, "rb") as f:
                        serialized_fn = deserialize_node_asset(f.read(), "function")

                    # Load args and kwargs
                    ser_args = []
                    ser_kwargs = {}

                    args_uris = [resources["inputs"][index] for index in args_ids]
                    for uri in args_uris:
                        if uri.startswith(prefix):
                            uri = uri[prefix_len:]
                        with open(uri, "rb") as f:
                            ser_args.append(deserialize_node_asset(f.read(), "output"))

                    kwargs_uris = {k: resources["inputs"][v] for k, v in kwargs_ids.items()}
                    for key, uri in kwargs_uris.items():
                        if uri.startswith(prefix):
                            uri = uri[prefix_len:]
                        with open(uri, "rb") as f:
                            ser_kwargs[key] = deserialize_node_asset(f.read(), "output")

                    # Load deps, call_before, and call_after
                    hooks_uri = resources["hooks"][task_id]
                    if hooks_uri.startswith(prefix):
                        hooks_uri = hooks_uri[prefix_len:]
                    with open(hooks_uri, "rb") as f:
                        hooks_json = deserialize_node_asset(f.read(), "hooks")
                    deps_json = hooks_json.get("deps", {})
                    call_before_json = hooks_json.get("call_before", [])
                    call_after_json = hooks_json.get("call_after", [])

                    # Assemble and invoke the task
                    call_before, call_after = _gather_deps(
                        deps_json, call_before_json, call_after_json
                    )

                    exception_occurred = False

                    # Run the task function
                    with set_context(dispatch_id, task_id):
                        transportable_output = wrapper_fn(
                            serialized_fn, call_before, call_after, *ser_args, **ser_kwargs
                        )

                    ser_output = serialize_node_asset(transportable_output, "output")

                    # Save output
                    with open(result_uri, "wb") as f:
                        f.write(ser_output)

                    # Save QElectron DB
                    qelectron_db_path = get_qelectron_db_path(dispatch_id, task_id)
                    if qelectron_db_path is not None:
                        with open(qelectron_db_path / "data.mdb", "rb") as f:
                            qelectron_db_bytes = f.read()

                    with open(qelectron_db_uri, "wb") as f:
                        f.write(qelectron_db_bytes)

                    resources["inputs"][task_id] = result_uri

                    output_size = len(ser_output)
                    qelectron_db_size = len(qelectron_db_bytes)
                    stdout.flush()
                    stderr.flush()
                    stdout_size = os.path.getsize(stdout_uri)
                    stderr_size = os.path.getsize(stderr_uri)
                    result_summary = {
                        "node_id": task_id,
                        "output": {
                            "uri": result_uri,
                            "size": output_size,
                        },
                        "stdout": {
                            "uri": stdout_uri,
                            "size": stdout_size,
                        },
                        "stderr": {
                            "uri": stderr_uri,
                            "size": stderr_size,
                        },
                        "qelectron_db": {
                            "uri": qelectron_db_uri,
                            "size": qelectron_db_size,
                        },
                        "exception_occurred": exception_occurred,
                    }

                except Exception as ex:
                    exception_occurred = True
                    tb = "".join(traceback.TracebackException.from_exception(ex).format())
                    print(tb, file=sys.stderr)
                    stdout.flush()
                    stderr.flush()
                    stdout_size = os.path.getsize(stdout_uri)
                    stderr_size = os.path.getsize(stderr_uri)
                    result_summary = {
                        "node_id": task_id,
                        "output": {
                            "uri": "",
                            "size": 0,
                        },
                        "stdout": {
                            "uri": stdout_uri,
                            "size": stdout_size,
                        },
                        "stderr": {
                            "uri": stderr_uri,
                            "size": stderr_size,
                        },
                        "qelectron_db": {
                            "uri": "",
                            "size": 0,
                        },
                        "exception_occurred": exception_occurred,
                    }

                    break

                finally:
                    results.append(result_summary)
                    result_path = os.path.join(results_dir, f"result-{dispatch_id}:{task_id}.json")

                    # Write the summary file containing the URIs for
                    # the serialized result, stdout, stderr, and qelectron_db
                    with open(result_path, "w") as f:
                        json.dump(result_summary, f)

    # Deal with any tasks that did not run
    n = len(results)
    if n < len(task_ids):
        for i in range(n, len(task_ids)):
            result_summary = {
                "node_id": task_id,
                "output": {
                    "uri": "",
                    "size": 0,
                },
                "stdout": {
                    "uri": "",
                    "size": 0,
                },
                "stderr": {
                    "uri": "",
                    "size": 0,
                },
                "qelectron_db": {
                    "uri": "",
                    "size": 0,
                },
                "exception_occurred": True,
            }

            results.append(result_summary)

            result_path = os.path.join(results_dir, f"result-{dispatch_id}:{task_id}.json")

            with open(result_path, "w") as f:
                json.dump(result_summary, f)
