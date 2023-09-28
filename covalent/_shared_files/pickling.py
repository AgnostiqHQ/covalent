# Copyright 2023 Agnostiq Inc.
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

# pylint: disable=invalid-name

"""Hopefully temporary custom tools to handle pickling and/or un-pickling."""

from contextlib import contextmanager
from typing import Any, Callable, Tuple

from pennylane.ops.qubit.observables import Projector

_PENNYLANE_METHOD_OVERRIDES = (
    # class, method_name, method_func
    (Projector, "__reduce__", lambda self: (Projector, (self.data[0], self.wires))),
)


def _qml_mods_pickle(func: Callable) -> Callable:
    """
    A decorator that applies overrides to select PennyLane objects, making them
    pickleable and/or un-pickleable in the local scope.
    """

    def _wrapper(*args, **kwargs):
        with _method_overrides(_PENNYLANE_METHOD_OVERRIDES):
            return func(*args, **kwargs)

    return _wrapper


@contextmanager
def _method_overrides(overrides: Tuple[Any, str, Callable]) -> None:
    """
    Creates a context where all `overrides` are applied on entry and un-applied on exit.
    """

    unapply_overrides = None
    try:
        unapply_overrides = _apply_method_overrides(overrides)
        yield
    finally:
        unapply_overrides()


def _apply_method_overrides(overrides: Tuple[Any, str, Callable]) -> Callable:
    """
    This function is called by the `_method_overrides()` context manager.

    It applies the overrides in `_METHOD_OVERRIDES` to the corresponding objects
    and returns a function that can later restore those objects.
    """

    restoration_list = []
    for cls, method_name, func in overrides:
        # Attribute will be deleted later if `attr` is a length-1 tuple.
        attr = (method_name,)
        if hasattr(cls, method_name):
            # Attribute will be restored later to the corresponding method.
            attr += (getattr(cls, method_name),)

        # Store attribute information.
        restoration_list.append(attr)

        # Use `func` to create or replace the method by name.
        setattr(cls, method_name, func)

    def _unapply_overrides():
        for attr in restoration_list:
            # Here `attr` is `(method_name,)` or `(method_name, original_func)`.
            if len(attr) == 1:
                # Delete attribute that did not exist before.
                delattr(cls, attr[0])
            else:
                # Restore original attribute.
                setattr(cls, attr[0], attr[1])

    return _unapply_overrides
