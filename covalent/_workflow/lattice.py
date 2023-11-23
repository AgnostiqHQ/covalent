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

"""Class corresponding to computation workflow."""

import importlib.metadata
import json
import os
import warnings
import webbrowser
from builtins import list
from contextlib import redirect_stdout
from copy import deepcopy
from dataclasses import asdict
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

from .._shared_files import logger
from .._shared_files.config import get_config
from .._shared_files.context_managers import active_lattice_manager
from .._shared_files.defaults import DefaultMetadataValues
from .._shared_files.utils import get_named_params, get_serialized_function_str, get_ui_url
from .depsbash import DepsBash
from .depscall import DepsCall
from .depspip import DepsPip
from .postprocessing import Postprocessor
from .transport import TransportableObject, _TransportGraph, encode_metadata

if TYPE_CHECKING:
    from .._results_manager.result import Result
    from ..executor import BaseExecutor
    from ..triggers import BaseTrigger

from .._shared_files.utils import get_imports, get_serialized_function_str

consumable_constraints = []

DEFAULT_METADATA_VALUES = asdict(DefaultMetadataValues())

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class Lattice:
    """
    A lattice workflow object that holds the work flow graph and is returned by :obj:`lattice <covalent.lattice>` decorator.

    Attributes:
        workflow_function: The workflow function that is decorated by :obj:`lattice <covalent.lattice>` decorator.
        transport_graph: The transport graph which will be the basis on how the workflow is executed.
        metadata: Dictionary of metadata of the lattice.
        post_processing: Boolean to indicate if the lattice is in post processing mode or not.
        kwargs: Keyword arguments passed to the workflow function.
        electron_outputs: Dictionary of electron outputs received after workflow execution.
    """

    def __init__(
        self, workflow_function: Callable, transport_graph: _TransportGraph = None
    ) -> None:
        self.workflow_function = workflow_function
        self.workflow_function_string = get_serialized_function_str(self.workflow_function)
        self.transport_graph = transport_graph or _TransportGraph()
        self.metadata = {}
        self.__name__ = self.workflow_function.__name__
        self.__doc__ = self.workflow_function.__doc__
        self.post_processing = False
        self.inputs = None
        self.named_args = None
        self.named_kwargs = None
        self.electron_outputs = {}
        self.lattice_imports, self.cova_imports = get_imports(self.workflow_function)

        self.workflow_function = TransportableObject.make_transportable(self.workflow_function)

        # Bound electrons are defined as electrons with a valid node_id, since it means they are bound to a TransportGraph.
        self._bound_electrons = {}  # Clear before serializing

        self.python_version = self.workflow_function.python_version
        self.covalent_version = importlib.metadata.version("covalent")

    # To be called after build_graph
    def serialize_to_json(self) -> str:
        attributes = deepcopy(self.__dict__)
        attributes["workflow_function"] = self.workflow_function.to_dict()

        attributes["metadata"] = encode_metadata(self.metadata)
        attributes["transport_graph"] = None
        if self.transport_graph:
            attributes["transport_graph"] = self.transport_graph.serialize_to_json()

        attributes["inputs"] = self.inputs.to_dict()
        attributes["named_args"] = self.named_args.to_dict()
        attributes["named_kwargs"] = self.named_kwargs.to_dict()

        attributes["electron_outputs"] = {}
        for node_name, output in self.electron_outputs.items():
            attributes["electron_outputs"][node_name] = output.to_dict()

        return json.dumps(attributes)

    @staticmethod
    def deserialize_from_json(json_data: str) -> None:
        attributes = json.loads(json_data)

        for node_name, object_dict in attributes["electron_outputs"].items():
            attributes["electron_outputs"][node_name] = TransportableObject.from_dict(object_dict)

        attributes["named_kwargs"] = TransportableObject.from_dict(attributes["named_kwargs"])
        attributes["named_args"] = TransportableObject.from_dict(attributes["named_args"])
        attributes["inputs"] = TransportableObject.from_dict(attributes["inputs"])

        if attributes["transport_graph"]:
            tg = _TransportGraph()
            tg.deserialize_from_json(attributes["transport_graph"])
            attributes["transport_graph"] = tg

        attributes["workflow_function"] = TransportableObject.from_dict(
            attributes["workflow_function"]
        )

        def dummy_function(x):
            return x

        lat = Lattice(dummy_function)
        lat.__dict__ = attributes
        return lat

    def set_metadata(self, name: str, value: Any) -> None:
        """
        Function to add/edit metadata of given name and value
        to lattice's metadata.

        Args:
            name: Name of the metadata to be added/edited.
            value: Value of the metadata to be added/edited.

        Returns:
            None
        """

        self.metadata[name] = value

    def get_metadata(self, name: str) -> Any:
        """
        Get value of the metadata of given name.

        Args:
            name: Name of the metadata whose value is needed.

        Returns:
            value: Value of the metadata of given name.

        Raises:
            KeyError: If metadata of given name is not present.
        """

        return self.metadata.get(name, None)

    @property
    def replace_electrons(self) -> Dict[str, Callable]:
        return self.__dict__.get("_replace_electrons", {})

    @property
    def task_packing(self) -> bool:
        return self.__dict__.get("_task_packing", False)

    def build_graph(self, *args, **kwargs) -> None:
        """
        Builds the transport graph for the lattice by executing the workflow
        function which will trigger the call of all underlying electrons and
        they will get added to the transport graph for later execution.

        Also redirects any print statements inside the lattice function to null
        and ignores any exceptions caused while executing the function.

        GRAPH WILL NOT BE BUILT AFTER AN EXCEPTION HAS OCCURRED.

        Args:
            *args: Positional arguments to be passed to the workflow function.
            **kwargs: Keyword arguments to be passed to the workflow function.

        Returns:
            None

        """

        self.transport_graph.reset()

        workflow_function = self.workflow_function.get_deserialized()

        named_args, named_kwargs = get_named_params(workflow_function, args, kwargs)
        new_args = [v for _, v in named_args.items()]
        new_kwargs = dict(named_kwargs.items())

        self.inputs = TransportableObject({"args": args, "kwargs": kwargs})
        self.named_args = TransportableObject(named_args)
        self.named_kwargs = TransportableObject(named_kwargs)
        self.lattice_imports, self.cova_imports = get_imports(workflow_function)

        # Set any lattice metadata not explicitly set by the user
        constraint_names = {"executor", "workflow_executor", "deps", "call_before", "call_after"}
        new_metadata = {
            name: DEFAULT_METADATA_VALUES[name]
            for name in constraint_names
            if self.metadata[name] is None
        }
        new_metadata = encode_metadata(new_metadata)

        for k, v in new_metadata.items():
            self.metadata[k] = v

        # Check whether task packing is enabled
        self._task_packing = get_config("sdk.task_packing") == "true"

        with redirect_stdout(open(os.devnull, "w")):
            with active_lattice_manager.claim(self):
                try:
                    retval = workflow_function(*new_args, **new_kwargs)
                except Exception:
                    warnings.warn(
                        "Please make sure you are not manipulating an object inside the lattice."
                    )
                    raise

        pp = Postprocessor(lattice=self)

        if get_config("sdk.exhaustive_postprocess") == "true":
            pp.add_exhaustive_postprocess_node(self._bound_electrons.copy())
        else:
            pp.add_reconstruct_postprocess_node(retval, self._bound_electrons.copy())

        self._bound_electrons = {}  # Reset bound electrons

        # Clear this temporary attribute
        del self.__dict__["_task_packing"]

    def draw(self, *args, **kwargs) -> None:
        """
        Generate lattice graph and display in UI taking into account passed in
        arguments.

        Args:
            *args: Positional arguments to be passed to build the graph.
            **kwargs: Keyword arguments to be passed to build the graph.

        Returns:
            None
        """

        import covalent_ui.result_webhook as result_webhook

        self.build_graph(*args, **kwargs)
        result_webhook.send_draw_request(self)
        draw_preview_url = get_ui_url("/preview")
        message = f"To preview the transport graph of the lattice, visit {draw_preview_url}"
        app_log.info(message)
        print(message)
        webbrowser.open(draw_preview_url)

    def __call__(self, *args, **kwargs):
        """Execute lattice as an ordinary function for testing purposes."""

        workflow_function = self.workflow_function.get_deserialized()
        return workflow_function(*args, **kwargs)

    def dispatch(self, *args, **kwargs) -> str:
        """
        DEPRECATED: Function to dispatch workflows.

        Args:
            *args: Positional arguments for the workflow
            **kwargs: Keyword arguments for the workflow

        Returns:
            Dispatch id assigned to job
        """

        app_log.warning(
            "workflow.dispatch(your_arguments_here) is deprecated and may get removed without notice in future releases. Please use covalent.dispatch(workflow)(your_arguments_here) instead.",
            exc_info=DeprecationWarning,
        )

        from .._dispatcher_plugins import local_dispatch

        return local_dispatch(self)(*args, **kwargs)

    def dispatch_sync(self, *args, **kwargs) -> "Result":
        """
        DEPRECATED: Function to dispatch workflows synchronously by waiting for the result too.

        Args:
            *args: Positional arguments for the workflow
            **kwargs: Keyword arguments for the workflow

        Returns:
            Result of workflow execution
        """

        app_log.warning(
            "workflow.dispatch_sync(your_arguments_here) is deprecated and may get removed without notice in future releases. Please use covalent.dispatch_sync(workflow)(your_arguments_here) instead.",
            exc_info=DeprecationWarning,
        )

        from .._dispatcher_plugins import local_dispatch_sync

        return local_dispatch_sync(self)(*args, **kwargs)


def lattice(
    _func: Optional[Callable] = None,
    *,
    backend: Optional[str] = None,
    executor: Optional[Union[List[Union[str, "BaseExecutor"]], Union[str, "BaseExecutor"]]] = None,
    workflow_executor: Optional[
        Union[List[Union[str, "BaseExecutor"]], Union[str, "BaseExecutor"]]
    ] = None,
    # Add custom metadata fields here
    deps_bash: Union[DepsBash, list, str] = None,
    deps_pip: Union[DepsPip, list] = None,
    call_before: Union[List[DepsCall], DepsCall] = None,
    call_after: Union[List[DepsCall], DepsCall] = None,
    triggers: Union["BaseTrigger", List["BaseTrigger"]] = None,
    # e.g. schedule: True, whether to use a custom scheduling logic or not
) -> Lattice:
    """
    Lattice decorator to be called upon a function. Returns a new `Lattice <covalent._workflow.lattice.Lattice>` object.

    Args:
        _func: function to be decorated

    Keyword Args:
        backend: DEPRECATED: Same as `executor`.
        executor: Alternative executor object to be used in the execution of each node. If not passed, the dask
            executor is used by default.
        workflow_executor: Executor for postprocessing the workflow. Defaults to the built-in dask executor or
            the local executor depending on whether Covalent is started with the `--no-cluster` option.
        deps_bash: An optional DepsBash object specifying a list of shell commands to run before `_func`
        deps_pip: An optional DepsPip object specifying a list of PyPI packages to install before running `_func`
        call_before: An optional list of DepsCall objects specifying python functions to invoke before the electron
        call_after: An optional list of DepsCall objects specifying python functions to invoke after the electron
        triggers: Any triggers that need to be attached to this lattice, default is None

    Returns:
        :obj:`Lattice <covalent._workflow.lattice.Lattice>` : Lattice object inside which the decorated function exists.
    """

    if backend:
        app_log.warning(
            "backend is deprecated and will be removed in a future release. Please use executor keyword instead.",
            exc_info=DeprecationWarning,
        )
        executor = backend

    deps = {}

    if isinstance(deps_bash, DepsBash):
        deps["bash"] = deps_bash
    if isinstance(deps_bash, (list, str)):
        deps["bash"] = DepsBash(commands=deps_bash)

    if isinstance(deps_pip, DepsPip):
        deps["pip"] = deps_pip
    if isinstance(deps_pip, list):
        deps["pip"] = DepsPip(packages=deps_pip)

    if isinstance(call_before, DepsCall):
        call_before = [call_before]

    if isinstance(call_after, DepsCall):
        call_after = [call_after]

    from ..triggers import BaseTrigger

    if isinstance(triggers, BaseTrigger):
        triggers = [triggers]

    constraints = {
        "executor": executor,
        "workflow_executor": workflow_executor,
        "deps": deps,
        "call_before": call_before,
        "call_after": call_after,
        "triggers": triggers,
    }

    constraints = encode_metadata(constraints)

    def decorator_lattice(func=None):
        @wraps(func)
        def wrapper_lattice(*args, **kwargs):
            lattice_object = Lattice(workflow_function=func)
            for k, v in constraints.items():
                lattice_object.set_metadata(k, v)
            lattice_object.transport_graph.lattice_metadata = lattice_object.metadata
            return lattice_object

        return wrapper_lattice()

    # Don't change the snippet below. This a subtle piece of logic that's best understood as is written.
    if _func is None:  # decorator is called with arguments
        return decorator_lattice
    else:  # decorator is called without arguments
        return decorator_lattice(_func)
