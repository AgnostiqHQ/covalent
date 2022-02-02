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

from .._shared_files import logger
from .._shared_files.context_managers import active_lattice_manager
from .._shared_files.defaults import (
    _DEFAULT_CONSTRAINT_VALUES,
    attr_prefix,
    electron_dict_prefix,
    electron_list_prefix,
    generator_prefix,
    parameter_prefix,
    sublattice_prefix,
    subscript_prefix,
)
from .._shared_files.utils import get_serialized_function_str
from .lattice import Lattice

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

    def __init__(
        self, function: Callable, node_id: int = None, metadata: dict = {}, **kwargs
    ) -> None:
        self.function = function
        self.node_id = node_id
        self.metadata = metadata
        self.kwargs = kwargs

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
                if hasattr(op1, "function"):
                    op1_name = op1.function.__name__
                op2_name = op2
                if hasattr(op2, "function"):
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
            active_lattice = active_lattice_manager.get_active_lattice()

            if active_lattice:
                try:
                    node_name = generator_prefix + self.function.__name__ + "()" + f"[{i}]"

                except AttributeError:
                    # The case when nested iter calls are made on the same electron
                    node_name = generator_prefix + active_lattice.transport_graph.get_node_value(
                        self.node_id, "name"
                    )
                    node_name += f"[{i}]"

                node_id = active_lattice.transport_graph.add_node(
                    kwargs={"key": i},
                    name=node_name,
                    function=None,
                    metadata=_DEFAULT_CONSTRAINT_VALUES.copy(),
                )

                active_lattice.transport_graph.add_edge(self.node_id, node_id, f"[{i}]")

                yield Electron(function=None, node_id=node_id, metadata=None, key=i)

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

        active_lattice = active_lattice_manager.get_active_lattice()

        if active_lattice:
            try:
                node_name = attr_prefix + self.function.__name__ + "." + attr
            except AttributeError:
                node_name = attr_prefix + active_lattice.transport_graph.get_node_value(
                    self.node_id, "name"
                )
                node_name += "." + attr

            node_id = active_lattice.transport_graph.add_node(
                kwargs={"attr": attr},
                name=node_name,
                function=None,
                metadata=_DEFAULT_CONSTRAINT_VALUES.copy(),
            )

            active_lattice.transport_graph.add_edge(self.node_id, node_id, f".{attr}")

            return Electron(function=None, node_id=node_id, metadata=None, attr=attr)

        return super().__getattr__(attr)

    def __getitem__(self, key: Union[int, str]) -> "Electron":

        active_lattice = active_lattice_manager.get_active_lattice()

        if active_lattice:
            try:
                node_name = subscript_prefix + self.function.__name__ + "()" + f"[{key}]"
            except AttributeError:
                # Nested subscripting calls are made on the same electron
                node_name = subscript_prefix + active_lattice.transport_graph.get_node_value(
                    self.node_id, "name"
                )
                node_name += f"[{key}]"

            node_id = active_lattice.transport_graph.add_node(
                kwargs={"key": key},
                name=node_name,
                function=None,
                metadata=_DEFAULT_CONSTRAINT_VALUES.copy(),
            )

            active_lattice.transport_graph.add_edge(self.node_id, node_id, f"[{key}]")

            return Electron(function=None, node_id=node_id, metadata=None, key=key)

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

        # Merging the args to kwargs to maintain consistency throughout the code
        if self.function:
            kwargs.update(dict(zip(list(inspect.signature(self.function).parameters), args)))

        if active_lattice.post_processing:
            key = [k for k in active_lattice.electron_outputs if f"{self.function.__name__}" in k][
                0
            ]

            if not key:
                raise ValueError(
                    "dispatch_id and lattice mismatch. Please try "
                    "again with the correct dispatch_id."
                )

            output = active_lattice.electron_outputs[key]
            del active_lattice.electron_outputs[key]
            return output

        # Setting metadata for default values according to lattice's metadata
        # If metadata is default, then set it to lattice's default
        for k in self.metadata:
            if (
                k not in consumable_constraints
                and self.get_metadata(k) is _DEFAULT_CONSTRAINT_VALUES[k]
            ):
                self.set_metadata(k, active_lattice.get_metadata(k))

        # Add a node to the transport graph of the active lattice
        self.node_id = active_lattice.transport_graph.add_node(
            kwargs=kwargs,
            name=sublattice_prefix + self.function.__name__
            if isinstance(self.function, Lattice)
            else self.function.__name__,
            function=self.function,
            metadata=self.metadata.copy(),
        )

        # Add function string
        active_lattice.transport_graph.set_node_value(
            self.node_id, "function_string", get_serialized_function_str(self.function)
        )

        for key, value in kwargs.items():
            self.add_node_for_nested_iterables(
                value, self.node_id, key, active_lattice.transport_graph
            )

        return Electron(
            self.function,
            metadata=self.metadata,
            node_id=self.node_id,
            **kwargs,
        )

    def add_node_to_graph(
        self, graph: "_TransportGraph", prefix: str, key: str, value: Iterable
    ) -> int:
        """
        Adds the node to lattice's transport graph in the case
        where a collection of electrons is passed as an argument
        to another electron.

        Args:
            graph: Transport graph of the lattice
            prefix: Prefix of the node
            key: Key of the node kwargs
            value: Value of the node kwargs

        Returns:
            node_id: Node id of the added node
        """

        @electron
        def to_electron_collection(**x):
            return list(x.values())[0]

        node_id = graph.add_node(
            kwargs={key: value},
            name=prefix,
            function=to_electron_collection,
            metadata=_DEFAULT_CONSTRAINT_VALUES.copy(),
        )

        graph.set_node_value(
            node_id, "function_string", get_serialized_function_str(to_electron_collection)
        )

        return node_id

    def add_node_for_nested_iterables(
        self,
        some_value: Union[Any, "Electron"],
        node_id: int,
        key: str,
        transport_graph: "_TransportGraph",
    ):
        """
        Adds a node along with connecting edges for all the arguments to the electron.

        Args:
            some_value: Value of the node kwarg
            node_id: Node number of the electron
            key: Key of the node kwarg
            transport_graph: Transport graph of the lattice

        Returns:
            None
        """

        if isinstance(some_value, Electron):
            transport_graph.add_edge(some_value.node_id, node_id, variable=key)

        elif isinstance(some_value, list):
            list_node = self.add_node_to_graph(
                transport_graph, electron_list_prefix, key, some_value
            )

            for v in some_value:
                self.add_node_for_nested_iterables(v, list_node, key, transport_graph)

            transport_graph.add_edge(list_node, node_id, variable=key)

        elif isinstance(some_value, dict):
            dict_node = self.add_node_to_graph(
                transport_graph, electron_dict_prefix, key, some_value
            )

            for k, v in some_value.items():
                self.add_node_for_nested_iterables(v, dict_node, k, transport_graph)

            transport_graph.add_edge(dict_node, node_id, variable=key)

        else:
            argument_kwargs = {key: some_value}
            argument_node = transport_graph.add_node(
                kwargs=argument_kwargs,
                name=parameter_prefix + str(some_value),
                function=None,
                metadata=_DEFAULT_CONSTRAINT_VALUES.copy(),
            )
            transport_graph.add_edge(argument_node, node_id, variable=key)


def electron(
    _func: Optional[Callable] = None,
    *,
    backend: Optional[
        Union[List[Union[str, "BaseExecutor"]], Union[str, "BaseExecutor"]]
    ] = _DEFAULT_CONSTRAINT_VALUES["backend"],
    # Add custom metadata fields here
) -> Callable:
    """Electron decorator to be called upon a function. Returns a new :obj:`Electron <covalent._workflow.electron.Electron>` object.

    Args:
        _func: function to be decorated

    Keyword Args:
        backend: Alternative executor object to be used by the electron execution. If not passed, the local
            executor is used by default.

    Returns:
        :obj:`Electron <covalent._workflow.electron.Electron>` : Electron object inside which the decorated function exists.
    """

    constraints = {
        "backend": backend,
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
