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

"""Class corresponding to computation nodes."""

import inspect
import operator
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Iterable, List, Optional, Union

from .._file_transfer.enums import Order
from .._file_transfer.file_transfer import FileTransfer
from .._shared_files import logger
from .._shared_files.context_managers import active_lattice_manager
from .._shared_files.defaults import (
    _DEFAULT_CONSTRAINT_VALUES,
    WAIT_EDGE_NAME,
    attr_prefix,
    electron_dict_prefix,
    electron_list_prefix,
    generator_prefix,
    parameter_prefix,
    prefix_separator,
    sublattice_prefix,
    subscript_prefix,
)
from .._shared_files.utils import get_named_params, get_serialized_function_str
from .depsbash import DepsBash
from .depscall import DepsCall
from .depspip import DepsPip
from .lattice import Lattice
from .transport import TransportableObject

consumable_constraints = ["budget", "time_limit"]

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
    """

    def __init__(self, function: Callable, node_id: int = None, metadata: dict = None) -> None:
        if metadata is None:
            metadata = {}
        self.function = function
        self.node_id = node_id
        self.metadata = metadata

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

        @electron
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

        return func_for_op(arg_1=operand_1, arg_2=operand_2)

    def __add__(self, other):
        return self.get_op_function(self, other, "+")

    def __radd__(self, other):
        return self.__add__(other)

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

    def __int__(self):
        return int()

    def __float__(self):
        return float()

    def __complex__(self):
        return complex()

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

                get_item_electron = Electron(function=get_item, metadata=self.metadata.copy())
                yield get_item_electron(self, i)

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
            get_attr_electron = Electron(function=get_attr, metadata=self.metadata.copy())
            return get_attr_electron(self, attr)

        return super().__getattr__(attr)

    def __getitem__(self, key: Union[int, str]) -> "Electron":

        if active_lattice := active_lattice_manager.get_active_lattice():

            def get_item(e, key):
                return e[key]

            get_item.__name__ = prefix_separator + self.function.__name__ + ".__getitem__"

            get_item_electron = Electron(function=get_item, metadata=self.metadata.copy())
            return get_item_electron(self, key)

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
        """

        # Check if inside a lattice and if not, perform a direct invocation of the function
        active_lattice = active_lattice_manager.get_active_lattice()
        if active_lattice is None:
            return self.function(*args, **kwargs)

        if active_lattice.post_processing:

            # This is to resolve `wait_for` calls during post processing time
            id, output = active_lattice.electron_outputs[0]

            for _, _, attr in active_lattice.transport_graph._graph.in_edges(id, data=True):
                if attr.get("wait_for"):
                    return Electron(function=None, metadata=None, node_id=id)

            active_lattice.electron_outputs.pop(0)
            return output.get_deserialized()

        # Setting metadata for default values according to lattice's metadata
        # If metadata is default, then set it to lattice's default
        for k in self.metadata:
            if (
                k not in consumable_constraints
                and k in _DEFAULT_CONSTRAINT_VALUES
                and self.get_metadata(k) is _DEFAULT_CONSTRAINT_VALUES[k]
            ):
                self.set_metadata(k, active_lattice.get_metadata(k))

        # Add a node to the transport graph of the active lattice
        self.node_id = active_lattice.transport_graph.add_node(
            name=sublattice_prefix + self.function.__name__
            if isinstance(self.function, Lattice)
            else self.function.__name__,
            function=self.function,
            metadata=self.metadata.copy(),
            function_string=get_serialized_function_str(self.function),
        )

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
            # Filter out kwargs to be injected by call_before calldeps at execution
            call_before = self.metadata["call_before"]
            retval_keywords = {item.retval_keyword: None for item in call_before}
            for key, value in named_kwargs.items():
                if key in retval_keywords:
                    app_log.debug(
                        f"kwarg {key} for function {self.function.__name__} to be injected at runtime"
                    )
                    continue

                self.connect_node_with_others(
                    self.node_id, key, value, "kwarg", None, active_lattice.transport_graph
                )

        return Electron(
            self.function,
            metadata=self.metadata,
            node_id=self.node_id,
        )

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

        if isinstance(param_value, Electron):
            transport_graph.add_edge(
                param_value.node_id,
                node_id,
                edge_name=param_name,
                param_type=param_type,
                arg_index=arg_index,
            )

        elif isinstance(param_value, list):
            list_node = self.add_collection_node_to_graph(transport_graph, electron_list_prefix)

            for index, v in enumerate(param_value):
                self.connect_node_with_others(
                    list_node, param_name, v, "kwarg", index, transport_graph
                )

            transport_graph.add_edge(
                list_node,
                node_id,
                edge_name=param_name,
                param_type=param_type,
                arg_index=arg_index,
            )

        elif isinstance(param_value, dict):
            dict_node = self.add_collection_node_to_graph(transport_graph, electron_dict_prefix)

            for k, v in param_value.items():
                self.connect_node_with_others(dict_node, k, v, "kwarg", None, transport_graph)

            transport_graph.add_edge(
                dict_node,
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
                metadata=_DEFAULT_CONSTRAINT_VALUES.copy(),
                value=encoded_param_value,
            )
            transport_graph.add_edge(
                parameter_node,
                node_id,
                edge_name=param_name,
                param_type=param_type,
                arg_index=arg_index,
            )

    def add_collection_node_to_graph(self, graph: "_TransportGraph", prefix: str) -> int:
        """
        Adds the node to lattice's transport graph in the case
        where a collection of electrons is passed as an argument
        to another electron.

        Args:
            graph: Transport graph of the lattice
            prefix: Prefix of the node

        Returns:
            node_id: Node id of the added node
        """

        @electron
        def to_decoded_electron_collection(**x):
            collection = list(x.values())[0]
            if isinstance(collection, list):
                return TransportableObject.deserialize_list(collection)
            elif isinstance(collection, dict):
                return TransportableObject.deserialize_dict(collection)

        node_id = graph.add_node(
            name=prefix,
            function=to_decoded_electron_collection,
            metadata=self.metadata.copy(),
            function_string=get_serialized_function_str(to_decoded_electron_collection),
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

        if active_lattice.post_processing:
            return active_lattice.electron_outputs.pop(0)[1]

        # Just using list(electrons) will not work since we are overriding the __iter__
        # method for an Electron which results in it essentially disappearing, thus using
        # [electrons] to create the list if there's a single electron
        electrons = [electrons] if isinstance(electrons, Electron) else list(electrons)

        for el in electrons:
            active_lattice.transport_graph.add_edge(
                el.node_id,
                self.node_id,
                edge_name=WAIT_EDGE_NAME,
                wait_for=True,
            )

        return Electron(
            self.function,
            metadata=self.metadata,
            node_id=self.node_id,
        )


def electron(
    _func: Optional[Callable] = None,
    *,
    backend: Optional[str] = None,
    executor: Optional[
        Union[List[Union[str, "BaseExecutor"]], Union[str, "BaseExecutor"]]
    ] = _DEFAULT_CONSTRAINT_VALUES["executor"],
    # Add custom metadata fields here
    files: List[FileTransfer] = [],
    deps_bash: Union[DepsBash, List, str] = _DEFAULT_CONSTRAINT_VALUES["deps"].get("bash", []),
    deps_pip: Union[DepsPip, list] = _DEFAULT_CONSTRAINT_VALUES["deps"].get("pip", None),
    call_before: Union[List[DepsCall], DepsCall] = _DEFAULT_CONSTRAINT_VALUES["call_before"],
    call_after: Union[List[DepsCall], DepsCall] = _DEFAULT_CONSTRAINT_VALUES["call_after"],
) -> Callable:
    """Electron decorator to be called upon a function. Returns the wrapper function with the same functionality as `_func`.

    Args:
        _func: function to be decorated

    Keyword Args:
        backend: DEPRECATED: Same as `executor`.
        executor: Alternative executor object to be used by the electron execution. If not passed, the dask
            executor is used by default.
        deps_bash: An optional DepsBash object specifying a list of shell commands to run before `_func`
        deps_pip: An optional DepsPip object specifying a list of PyPI packages to install before running `_func`
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

    deps = {}

    if isinstance(deps_bash, DepsBash):
        deps["bash"] = deps_bash
    if isinstance(deps_bash, list) or isinstance(deps_bash, str):
        deps["bash"] = DepsBash(commands=deps_bash)

    internal_call_before_deps = []
    internal_call_after_deps = []

    for file_transfer in files:
        _callback_ = file_transfer.cp()
        if file_transfer.order == Order.AFTER:
            internal_call_after_deps.append(DepsCall(_callback_))
        else:
            internal_call_before_deps.append(DepsCall(_callback_))

    if isinstance(deps_pip, DepsPip):
        deps["pip"] = deps_pip
    if isinstance(deps_pip, list):
        deps["pip"] = DepsPip(packages=deps_pip)

    if isinstance(call_before, DepsCall):
        call_before = [call_before]

    if isinstance(call_after, DepsCall):
        call_after = [call_after]

    call_before = internal_call_before_deps + call_before
    call_after = internal_call_after_deps + call_after

    constraints = {
        "executor": executor,
        "deps": deps,
        "call_before": call_before,
        "call_after": call_after,
    }

    def decorator_electron(func=None):
        @wraps(func)
        def wrapper(*args, **kwargs):
            electron_object = Electron(func)
            for k, v in constraints.items():
                electron_object.set_metadata(k, v)
            electron_object.__doc__ = func.__doc__
            return electron_object(*args, **kwargs)

        return wrapper

    if _func is None:  # decorator is called with arguments
        return decorator_electron
    else:  # decorator is called without arguments
        return decorator_electron(_func)
