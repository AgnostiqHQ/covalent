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

"""Class corresponding to computation nodes."""

import inspect
import json
import operator
import tempfile
from builtins import list
from copy import deepcopy
from dataclasses import asdict
from functools import wraps
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Optional, Union

from covalent._dispatcher_plugins.local import LocalDispatcher

from .._file_transfer.enums import Order
from .._file_transfer.file_transfer import FileTransfer
from .._shared_files import logger
from .._shared_files.context_managers import active_lattice_manager
from .._shared_files.defaults import (
    WAIT_EDGE_NAME,
    DefaultMetadataValues,
    electron_dict_prefix,
    electron_list_prefix,
    parameter_prefix,
    prefix_separator,
    sublattice_prefix,
)
from .._shared_files.util_classes import RESULT_STATUS
from .._shared_files.utils import (
    filter_null_metadata,
    get_named_params,
    get_serialized_function_str,
)
from .depsbash import DepsBash
from .depscall import RESERVED_RETVAL_KEY__FILES, DepsCall
from .depsmodule import DepsModule
from .depspip import DepsPip
from .lattice import Lattice
from .transport import TransportableObject, encode_metadata

consumable_constraints = ["budget", "time_limit"]

DEFAULT_METADATA_VALUES = asdict(DefaultMetadataValues())

if TYPE_CHECKING:
    from ..executor import BaseExecutor
    from .transport import _TransportGraph

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class Electron:
    """
    An electron (or task) object that is a modular component of a
    work flow and is returned by :obj:`electron <covalent.electron>`.

    Attributes:
        function: Function to be executed.
        node_id: Node id of the electron.
        metadata: Metadata to be used for the function execution.
        kwargs: Keyword arguments if any.
        task_group_id: the group to which the task be assigned when it is bound to a graph node. If unset, the group id will default to node id.
        packing_tasks: Flag to indicate whether task packing is enabled.
    """

    def __init__(
        self,
        function: Callable,
        node_id: int = None,
        metadata: dict = None,
        task_group_id: int = None,
        packing_tasks: bool = False,
    ) -> None:
        if metadata is None:
            metadata = {}
        self.function = function
        self.node_id = node_id
        self.metadata = metadata
        self.task_group_id = task_group_id
        self._packing_tasks = packing_tasks
        self._function_string = get_serialized_function_str(function)

    @property
    def packing_tasks(self) -> bool:
        return self._packing_tasks

    def set_metadata(self, name: str, value: Any) -> None:
        """
        Function to add/edit metadata of given name and value
        to electron's metadata.

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

        return self.metadata[name]

    def get_op_function(
        self, operand_1: Union[Any, "Electron"], operand_2: Union[Any, "Electron"], op: str
    ) -> "Electron":
        """
        Function to handle binary operations with electrons as operands.
        This will not execute the operation but rather create another electron
        which will be postponed to be executed according to the default electron
        configuration/metadata.

        This also makes sure that if these operations are being performed outside
        of a lattice, then they are performed as is.

        Args:
            operand_1: First operand of the binary operation.
            operand_2: Second operand of the binary operation.
            op: Operator to be used in the binary operation.

        Returns:
            electron: Electron object corresponding to the operation execution.
                      Behaves as a normal function call if outside a lattice.
        """
        op_table = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
            "**": operator.pow,
        }

        def rename(op1: Any, op: str, op2: Any) -> Callable:
            """
            Decorator to rename a function according
            to the operation being performed.

            Args:
                op1: First operand
                op: Operator
                op2: Second operand

            Returns:
                function: Renamed decorated function.
            """

            def decorator(f):
                op1_name = op1
                if hasattr(op1, "function") and op1.function:
                    op1_name = op1.function.__name__
                op2_name = op2
                if hasattr(op2, "function") and op2.function:
                    op2_name = op2.function.__name__

                f.__name__ = f"{op1_name}_{op}_{op2_name}"
                return f

            return decorator

        @rename(operand_1, op, operand_2)
        def func_for_op(arg_1: Union[Any, "Electron"], arg_2: Union[Any, "Electron"]) -> Any:
            """
            Intermediate function for the binary operation.

            Args:
                arg_1: First operand
                arg_2: Second operand

            Returns:
                result: Result of the binary operation.
            """

            return op_table[op](arg_1, arg_2)

        # Mint an arithmetic electron and execute it using the
        # enclosing lattice's workflow_executor.

        metadata = encode_metadata(DEFAULT_METADATA_VALUES.copy())
        executor = metadata["workflow_executor"]
        executor_data = metadata["workflow_executor_data"]

        op_electron = Electron(func_for_op, metadata=metadata)

        if active_lattice := active_lattice_manager.get_active_lattice():
            executor = active_lattice.metadata.get(
                "workflow_executor", metadata["workflow_executor"]
            )
            executor_data = active_lattice.metadata.get(
                "workflow_executor_data", metadata["workflow_executor_data"]
            )
            op_electron.metadata["executor"] = executor
            op_electron.metadata["executor_data"] = executor_data

        return op_electron(arg_1=operand_1, arg_2=operand_2)

    def __add__(self, other):
        return self.get_op_function(self, other, "+")

    def __radd__(self, other):
        return self.get_op_function(other, self, "+")

    def __sub__(self, other):
        return self.get_op_function(self, other, "-")

    def __rsub__(self, other):
        return self.get_op_function(other, self, "-")

    def __mul__(self, other):
        return self.get_op_function(self, other, "*")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self.get_op_function(self, other, "/")

    def __rtruediv__(self, other):
        return self.get_op_function(other, self, "/")

    def __pow__(self, other):
        return self.get_op_function(self, other, "**")

    def __int__(self):
        return int()

    def __float__(self):
        return float()

    def __complex__(self):
        return complex()

    def _get_collection_electron(self, name: str, func: Callable, metadata: Dict) -> "Electron":
        """Get collection electron with task packing enabled.

        Args:
            name: Name of the collection node.
            func: Function to be executed.

        Returns:
            Electron object with task packing enabled.

        """

        active_lattice = active_lattice_manager.get_active_lattice()
        return (
            Electron(function=func, metadata=self.metadata.copy())
            if name.startswith(sublattice_prefix)
            else Electron(
                function=func,
                metadata=metadata,
                task_group_id=self.task_group_id,
                packing_tasks=True and active_lattice.task_packing,
            )
        )

    def __iter__(self):
        last_frame = inspect.currentframe().f_back
        bytecode = last_frame.f_code.co_code
        expected_unpack_values = bytecode[last_frame.f_lasti + 1]

        if expected_unpack_values < 2:
            return

        for i in range(expected_unpack_values):
            if active_lattice := active_lattice_manager.get_active_lattice():
                try:
                    node_name = prefix_separator + self.function.__name__ + "()" + f"[{i}]"

                except AttributeError:
                    # The case when nested iter calls are made on the same electron
                    node_name = prefix_separator + active_lattice.transport_graph.get_node_value(
                        self.node_id, "name"
                    )
                    node_name += f"[{i}]"

                def get_item(e, key):
                    return e[key]

                get_item.__name__ = node_name

                # Perform a deep copy so as to not modify the parent
                # electron's hooks
                iterable_metadata = deepcopy(self.metadata)

                filtered_call_before = []
                if "call_before" in iterable_metadata["hooks"]:
                    for elem in iterable_metadata["hooks"]["call_before"]:
                        if elem["attributes"]["retval_keyword"] != "files":
                            filtered_call_before.append(elem)
                    iterable_metadata["hooks"]["call_before"] = filtered_call_before

                # Pack with main electron unless it is a sublattice.
                name = active_lattice.transport_graph.get_node_value(self.node_id, "name")
                yield self._get_collection_electron(name, get_item, iterable_metadata)(self, i)

    def __getattr__(self, attr: str) -> "Electron":
        # This is to handle the cases where magic functions are attempted
        # to be accessed. For example, in the case of pickling, sometimes
        # __getstate__ is called and we don't want to return an electron
        # object in that case.
        if attr.startswith("__") and attr.endswith("__"):
            return super().__getattr__(attr)

        if attr == "keys":
            raise AttributeError(
                "`keys` attribute should not be used in Electron objects due to conflict with `dict.keys`",
                "Please change the name of the attribute you want to use.",
            )

        if active_lattice := active_lattice_manager.get_active_lattice():

            def get_attr(e, attr):
                return getattr(e, attr)

            get_attr.__name__ = prefix_separator + self.function.__name__ + ".__getattr__"

            # Pack with main electron except for sublattices
            name = active_lattice.transport_graph.get_node_value(self.node_id, "name")
            metadata = self.metadata.copy()
            bound_electron = self._get_collection_electron(name, get_attr, metadata)(self, attr)
            return bound_electron

        return super().__getattr__(attr)

    def __getitem__(self, key: Union[int, str]) -> "Electron":
        if active_lattice := active_lattice_manager.get_active_lattice():

            def get_item(e, key):
                return e[key]

            get_item.__name__ = prefix_separator + self.function.__name__ + ".__getitem__"
            name = active_lattice.transport_graph.get_node_value(self.node_id, "name")
            metadata = self.metadata.copy()
            return self._get_collection_electron(name, get_item, metadata)(self, key)

        raise StopIteration

    def __call__(self, *args, **kwargs) -> Union[Any, "Electron"]:
        """
        Function to execute the electron.

        This behaves differently if the execution call is made inside a lattice
        and just adds the electron as a node to the lattice's transport graph.

        If the execution call is made outside of a lattice, then it executes the
        electron as a normal function call.

        Also contains a postprocessing part where the lattice's function is executed
        after all the nodes in the lattice's transport graph are executed. Then the
        execution call to the electron is replaced by its corresponding result.

        Note: Bound electrons are defined as electrons with a valid node_id, since it means they are bound to a TransportGraph.
        """

        # Check if inside a lattice and if not, perform a direct invocation of the function
        active_lattice = active_lattice_manager.get_active_lattice()
        if active_lattice is None:
            return self.function(*args, **kwargs)

        if active_lattice.post_processing:
            output = active_lattice.electron_outputs[0]
            active_lattice.electron_outputs.pop(0)
            return output

        # Setting metadata for default values according to lattice's metadata.
        for k in self.metadata:
            if (
                k not in consumable_constraints
                and k in DEFAULT_METADATA_VALUES
                and self.get_metadata(k) is None
            ):
                meta = active_lattice.get_metadata(k) or DEFAULT_METADATA_VALUES[k]
                self.set_metadata(k, meta)

        # Handle replace_electrons for redispatch
        name = self.function.__name__
        if name in active_lattice.replace_electrons:
            # Temporarily pop the replacement to avoid infinite
            # recursion.
            replacement_electron = active_lattice.replace_electrons.pop(name)

            # TODO: check that replacement has the same
            # signature. Also, although electron -> sublattice or
            # sublattice -> electron are technically possible, these
            # replacements will not work with the "exhaustive"
            # postprocess method which requires that the number of nodes be
            # determined by the lattice inputs.

            # This will return a bound replacement electron
            bound_electron = replacement_electron(*args, **kwargs)
            active_lattice.transport_graph.set_node_value(
                bound_electron.node_id,
                "status",
                RESULT_STATUS.PENDING_REPLACEMENT,
            )

            active_lattice.replace_electrons[name] = replacement_electron
            return bound_electron

        # Avoid direct attribute access since that might trigger
        # Electron.__getattr__ when executors build sublattices
        # constructed with older versions of Covalent
        function_string = self.__dict__.get("_function_string")

        # Handle sublattices by injecting _build_sublattice_graph node
        if isinstance(self.function, Lattice):
            parent_metadata = active_lattice.metadata.copy()
            app_log.debug(f"Parent lattice metadata: {parent_metadata}")
            e_meta = parent_metadata.copy()
            e_meta["executor"] = e_meta.pop("workflow_executor")
            e_meta["executor_data"] = e_meta.pop("workflow_executor_data")

            sub_electron = Electron(
                function=_build_sublattice_graph,
                metadata=e_meta,
            )

            name = sublattice_prefix + self.function.__name__
            bound_electron = sub_electron(
                self.function, json.dumps(parent_metadata), *args, **kwargs
            )

            active_lattice.transport_graph.set_node_value(bound_electron.node_id, "name", name)
            active_lattice.transport_graph.set_node_value(
                bound_electron.node_id,
                "function_string",
                function_string,
            )

            return bound_electron

        # Add a node to the transport graph of the active lattice. Electrons bound to nodes will never be packed with the
        # 'master' Electron. # Add non-sublattice node to the transport graph of the active lattice.

        self.node_id = active_lattice.transport_graph.add_node(
            name=self.function.__name__,
            function=self.function,
            metadata=self.metadata.copy(),
            function_string=function_string,
            task_group_id=self.task_group_id if self.packing_tasks else None,
        )
        self.task_group_id = self.task_group_id if self.packing_tasks else self.node_id

        if self.function:
            named_args, named_kwargs = get_named_params(self.function, args, kwargs)

            # For positional arguments
            # We use the fact that as of Python 3.6, dict order == insertion order
            for arg_index, item in enumerate(named_args.items()):
                key, value = item
                self.connect_node_with_others(
                    self.node_id, key, value, "arg", arg_index, active_lattice.transport_graph
                )

            # For keyword arguments
            # Filter out kwargs to be injected by call_before call_deps during execution.

            retval_keywords = {}
            if "call_before" in self.metadata["hooks"]:
                call_before = self.metadata["hooks"]["call_before"]
                retval_keywords = {
                    item["attributes"]["retval_keyword"]: None for item in call_before
                }

            for key, value in named_kwargs.items():
                if key in retval_keywords:
                    app_log.debug(
                        f"kwarg {key} for function {self.function.__name__} to be injected at runtime"
                    )
                    continue
                self.connect_node_with_others(
                    self.node_id, key, value, "kwarg", None, active_lattice.transport_graph
                )

        bound_electron = Electron(
            self.function,
            metadata=self.metadata,
            node_id=self.node_id,
            task_group_id=self.task_group_id,
            packing_tasks=self.packing_tasks,
        )
        active_lattice._bound_electrons[self.node_id] = bound_electron
        return bound_electron

    def connect_node_with_others(
        self,
        node_id: int,
        param_name: str,
        param_value: Union[Any, "Electron"],
        param_type: str,
        arg_index: int,
        transport_graph: "_TransportGraph",
    ):
        """
        Adds a node along with connecting edges for all the arguments to the electron.

        Args:
            node_id: Node number of the electron
            param_name: Name of the parameter
            param_value: Value of the parameter
            param_type: Type of parameter, positional or keyword
            transport_graph: Transport graph of the lattice

        Returns:
            None
        """

        collection_metadata = encode_metadata(DEFAULT_METADATA_VALUES.copy())
        active_lattice = active_lattice_manager.get_active_lattice()

        if "executor" in self.metadata:
            collection_metadata["executor"] = self.metadata["executor"]
            collection_metadata["executor_data"] = self.metadata["executor_data"]

        if isinstance(param_value, Electron):
            transport_graph.add_edge(
                param_value.node_id,
                node_id,
                edge_name=param_name,
                param_type=param_type,
                arg_index=arg_index,
            )

        elif isinstance(param_value, (list, tuple, set)):
            # Tuples and sets will also be converted to lists
            def _auto_list_node(*args, **kwargs):
                return list(args)

            list_electron = Electron(
                function=_auto_list_node,
                metadata=collection_metadata,
                task_group_id=self.task_group_id,
                packing_tasks=True and active_lattice.task_packing,
            )  # Group the auto-generated node with the main node.
            bound_electron = list_electron(*param_value)
            transport_graph.set_node_value(bound_electron.node_id, "name", electron_list_prefix)
            transport_graph.add_edge(
                list_electron.node_id,
                node_id,
                edge_name=param_name,
                param_type=param_type,
                arg_index=arg_index,
            )

        elif isinstance(param_value, dict):

            def _auto_dict_node(keys, values):
                return {keys[i]: values[i] for i in range(len(keys))}

            dict_electron = Electron(
                function=_auto_dict_node,
                metadata=collection_metadata,
                task_group_id=self.task_group_id,
                packing_tasks=True and active_lattice.task_packing,
            )  # Group the auto-generated node with the main node.
            bound_electron = dict_electron(list(param_value.keys()), list(param_value.values()))
            transport_graph.set_node_value(bound_electron.node_id, "name", electron_dict_prefix)
            transport_graph.add_edge(
                dict_electron.node_id,
                node_id,
                edge_name=param_name,
                param_type=param_type,
                arg_index=arg_index,
            )

        else:
            encoded_param_value = TransportableObject.make_transportable(param_value)

            parameter_node = transport_graph.add_node(
                name=parameter_prefix + str(param_value),
                function=None,
                metadata=encode_metadata(DEFAULT_METADATA_VALUES.copy()),
                value=encoded_param_value,
                output=encoded_param_value,
            )
            transport_graph.add_edge(
                parameter_node,
                node_id,
                edge_name=param_name,
                param_type=param_type,
                arg_index=arg_index,
            )

        return node_id

    def wait_for(self, electrons: Union["Electron", Iterable["Electron"]]):
        """
        Waits for the given electrons to complete before executing this one.
        Adds the necessary edges between this and those electrons without explicitly
        connecting their inputs/outputs.

        Useful when execution of this electron relies on a side-effect from the another one.

        Args:
            electrons: Electron(s) which will be waited for to complete execution
                       before starting execution for this one

        Returns:
            Electron
        """

        active_lattice = active_lattice_manager.get_active_lattice()

        # Just using list(electrons) will not work since we are overriding the __iter__
        # method for an Electron which results in it essentially disappearing, thus using
        # [electrons] to create the list if there's a single electron
        electrons = [electrons] if isinstance(electrons, Electron) else list(electrons)

        for el in electrons:
            active_lattice.transport_graph.add_edge(
                el.node_id,
                self.node_id,
                edge_name=WAIT_EDGE_NAME,
            )

        return Electron(
            self.function,
            metadata=self.metadata,
            node_id=self.node_id,
        )

    @property
    def as_transportable_dict(self) -> Dict:
        """Get transportable electron object and metadata."""
        return {
            "name": self.function.__name__,
            "function": TransportableObject(self.function).to_dict(),
            "function_string": get_serialized_function_str(self.function),
            "metadata": filter_null_metadata(self.metadata),
        }


# Dynamically adding properties to the Electron class
# This is being done this way so that it's easier to add
# or remove properties in the future without having to
# edit the class definition itself.
Electron.executor = property(lambda self: self.get_metadata("executor"))
Electron.executor = Electron.executor.setter(
    lambda self, value: self.metadata.update(encode_metadata({"executor": value}))
)


def electron(
    _func: Optional[Callable] = None,
    *,
    backend: Optional[str] = None,
    executor: Optional[Union[List[Union[str, "BaseExecutor"]], Union[str, "BaseExecutor"]]] = None,
    # Add custom metadata fields here
    files: List[FileTransfer] = [],
    deps_bash: Union[DepsBash, List, str] = None,
    deps_pip: Union[DepsPip, list] = None,
    deps_module: Union[DepsModule, List[DepsModule], str, List[str]] = None,
    call_before: Union[List[DepsCall], DepsCall] = None,
    call_after: Union[List[DepsCall], DepsCall] = None,
) -> Callable:  # sourcery skip: assign-if-exp
    """
    Electron decorator to be called upon a function. Returns the wrapper function with the same functionality as `_func`.

    Args:
        _func: function to be decorated

    Keyword Args:
        backend: DEPRECATED: Same as `executor`.
        executor: Alternative executor object to be used by the electron execution. If not passed, the dask
            executor is used by default.
        deps_bash: An optional DepsBash object specifying a list of shell commands to run before `_func`
        deps_pip: An optional DepsPip object specifying a list of PyPI packages to install before running `_func`
        deps_module: An optional DepsModule (or similar) object specifying which user modules to load before running `_func`
        call_before: An optional list of DepsCall objects specifying python functions to invoke before the electron
        call_after: An optional list of DepsCall objects specifying python functions to invoke after the electron
        files: An optional list of FileTransfer objects which copy files to/from remote or local filesystems.

    Returns:
        :obj:`Electron <covalent._workflow.electron.Electron>` : Electron object inside which the decorated function exists.

    """

    if backend:
        app_log.warning(
            "backend is deprecated and will be removed in a future release. Please use executor keyword instead.",
            exc_info=DeprecationWarning,
        )
        executor = backend

    deps = {} if deps_bash or deps_pip else None

    if isinstance(deps_bash, DepsBash):
        deps["bash"] = deps_bash
    if isinstance(deps_bash, (list, str)):
        deps["bash"] = DepsBash(commands=deps_bash)

    internal_call_before_deps = []
    internal_call_after_deps = []

    if files:
        for file_transfer in files:
            _file_transfer_pre_hook_, _file_transfer_call_dep_ = file_transfer.cp()

            # pre-file transfer hook to create any necessary temporary files
            internal_call_before_deps.append(
                DepsCall(
                    _file_transfer_pre_hook_,
                    retval_keyword=RESERVED_RETVAL_KEY__FILES,
                    override_reserved_retval_keys=True,
                )
            )

            if file_transfer.order == Order.AFTER:
                internal_call_after_deps.append(DepsCall(_file_transfer_call_dep_))
            else:
                internal_call_before_deps.append(DepsCall(_file_transfer_call_dep_))

    if deps_module:
        if isinstance(deps_module, list):
            # Convert to DepsModule objects
            converted_deps = []
            for dep in deps_module:
                if type(dep) in [str, ModuleType]:
                    converted_deps.append(DepsModule(dep))
                else:
                    converted_deps.append(dep)
            deps_module = converted_deps

        elif type(deps_module) in [str, ModuleType]:
            deps_module = [DepsModule(deps_module)]

        elif isinstance(deps_module, DepsModule):
            deps_module = [deps_module]

        internal_call_before_deps.extend(deps_module)

    if isinstance(deps_pip, DepsPip):
        deps["pip"] = deps_pip
    if isinstance(deps_pip, list):
        deps["pip"] = DepsPip(packages=deps_pip)

    if isinstance(call_before, DepsCall):
        call_before = [call_before]

    if isinstance(call_after, DepsCall):
        call_after = [call_after]

    call_before_final = [] if internal_call_before_deps or call_before else None
    if internal_call_before_deps:
        call_before_final.extend(internal_call_before_deps)
    if call_before:
        call_before_final.extend(call_before)

    call_after_final = [] if internal_call_after_deps or call_after else None
    if internal_call_after_deps:
        call_after_final.extend(internal_call_after_deps)
    if call_after:
        call_after_final.extend(call_after)

    if deps is None and call_before_final is None and call_after_final is None:
        hooks = None
    else:
        hooks = {}
        if deps is not None:
            hooks["deps"] = deps
        if call_before_final is not None:
            hooks["call_before"] = call_before_final
        if call_after_final is not None:
            hooks["call_after"] = call_after_final

    constraints = {
        "executor": executor,
        "hooks": hooks,
    }
    constraints = encode_metadata(constraints)

    def decorator_electron(func=None):
        """
        Electron decorator function. Note that the electron_object
        defined below is an example of an unbound electron, i.e.
        electron without a node id.

        """

        electron_object = Electron(func)
        for k, v in constraints.items():
            electron_object.set_metadata(k, v)
        electron_object.__doc__ = func.__doc__

        @wraps(func)
        def wrapper(*args, **kwargs):
            return electron_object(*args, **kwargs)

        wrapper.electron_object = electron_object

        return wrapper

    if _func is None:  # decorator is called with arguments
        return decorator_electron
    else:  # decorator is called without arguments
        return decorator_electron(_func)


def wait(child, parents):
    """Instructs Covalent that an electron should wait for some other
    tasks to complete before it is dispatched.

    Args:
        child: the dependent electron
        parents: Electron(s) which must complete before `waiting_electron` starts

    Returns:
        waiting_electron

    Useful when execution of an electron relies on a side-effect
    from another one.

    """
    active_lattice = active_lattice_manager.get_active_lattice()

    if active_lattice and not active_lattice.post_processing:
        return child.wait_for(parents)
    else:
        return child


# Copied from runner.py
def _build_sublattice_graph(sub: Lattice, json_parent_metadata: str, *args, **kwargs):
    import os

    parent_metadata = json.loads(json_parent_metadata)
    for k in sub.metadata.keys():
        if not sub.metadata[k] and k != "triggers":
            sub.metadata[k] = parent_metadata[k]

    sub.build_graph(*args, **kwargs)

    DISABLE_LEGACY_SUBLATTICES = os.environ.get("COVALENT_DISABLE_LEGACY_SUBLATTICES") == "1"

    try:
        # Attempt multistage sublattice dispatch.

        with tempfile.TemporaryDirectory(prefix="covalent-") as staging_path:
            # Try depositing the assets in a location readable by Covalent and
            # request Covalent to pull those assets.
            staging_uri_prefix = os.environ.get("COVALENT_STAGING_URI_PREFIX", None)
            manifest = LocalDispatcher.prepare_manifest(sub, staging_path)
            recv_manifest = manifest

            # If the executor can reach the Covalent server directly,
            # submit the sublattice dispatch to Covalent but don't start it.
            if not staging_uri_prefix:
                parent_dispatch_id = os.environ["COVALENT_DISPATCH_ID"]
                dispatcher_url = os.environ["COVALENT_DISPATCHER_URL"]
                recv_manifest = LocalDispatcher.register_manifest(
                    manifest,
                    dispatcher_addr=dispatcher_url,
                    parent_dispatch_id=parent_dispatch_id,
                    push_assets=True,
                )
                LocalDispatcher.upload_assets(recv_manifest)

            return recv_manifest.model_dump_json()

    except Exception as ex:
        # Fall back to legacy sublattice handling
        if DISABLE_LEGACY_SUBLATTICES:
            raise
        print("Falling back to legacy sublattice handling")
        return sub.serialize_to_json()
