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

from copy import deepcopy

from .deps import Deps
from .transport import TransportableObject

RESERVED_RETVAL_KEY__FILES = "files"


class DepsCall(Deps):
    """Functions, shell commands, PyPI packages, and other types of dependencies to be called in an electron's execution environment

    Deps class to encapsulate python functions to be
    called in the same execution environment as the electron.

    Attributes:
        func: A callable
        args: args list
        kwargs: kwargs dict
        retval_keyword: An optional string referencing the return value of func.

    If retval_keyword is specified, the return value of func will be
    passed during workflow execution as an argument to the electron
    corresponding to the parameter of the same name.

    Notes:
        Electron parameters to be injected during execution must have default
        parameter values.

        It is the user's responsibility to ensure that `retval_keyword` is
        actually a parameter of the electron. Unexpected behavior may occur
        otherwise.

    """

    def __init__(
        self,
        func=None,
        args=[],
        kwargs={},
        *,
        retval_keyword="",
        override_reserved_retval_keys=False,
    ):

        if not override_reserved_retval_keys and retval_keyword in [RESERVED_RETVAL_KEY__FILES]:
            raise Exception(
                f"The retval_keyword for the specified DepsCall uses the reserved value '{retval_keyword}' please re-name to use another return value keyword."
            )

        super().__init__(
            apply_fn=func, apply_args=args, apply_kwargs=kwargs, retval_keyword=retval_keyword
        )

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary representation of self"""
        attributes = self.__dict__.copy()
        for k, v in attributes.items():
            if isinstance(v, TransportableObject):
                attributes[k] = v.to_dict()
            else:
                attributes[k] = v
        return {"type": "DepsCall", "short_name": self.short_name(), "attributes": attributes}

    def from_dict(self, object_dict) -> "DepsCall":
        """Rehydrate a dictionary representation

        Args:
            object_dict: a dictionary representation returned by `to_dict`

        Returns:
            self

        Instance attributes will be overwritten.
        """

        if not object_dict:
            return self

        attributes = deepcopy(object_dict["attributes"])
        for k, v in attributes.items():
            if isinstance(v, dict) and v.get("type") == "TransportableObject":
                attributes[k] = TransportableObject.from_dict(v)
        self.__dict__ = attributes
        return self
