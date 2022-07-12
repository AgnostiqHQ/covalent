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

"""Utility functions for covalent dispatcher"""

from typing import List, Tuple

from covalent._shared_files import logger
from covalent._workflow.transport import TransportableObject

app_log = logger.app_log
log_stack_info = logger.log_stack_info


def wrapper_fn(
    function: TransportableObject,
    call_before: List[Tuple[TransportableObject, TransportableObject, TransportableObject]],
    call_after: List[Tuple[TransportableObject, TransportableObject, TransportableObject]],
    *args,
    **kwargs,
):
    """
    Wrapper for serialized callable.

    Execute preparatory shell commands before deserializing and
    running the callable. This is the actual function to be sent to
    the various executors.

    """

    app_log.debug("Invoking call_before")
    for tup in call_before:
        serialized_fn, serialized_args, serialized_kwargs = tup
        cb_fn = serialized_fn.get_deserialized()
        cb_args = serialized_args.get_deserialized()
        cb_kwargs = serialized_kwargs.get_deserialized()
        app_log.debug(f"Invoking ({cb_fn}, args={cb_args}, kwargs={cb_kwargs}")
        cb_fn(*cb_args, **cb_kwargs)

    fn = function.get_deserialized()
    output = fn(*args, **kwargs)

    app_log.debug("Invoking call_after")
    for tup in call_after:
        serialized_fn, serialized_args, serialized_kwargs = tup
        ca_fn = serialized_fn.get_deserialized()
        ca_args = serialized_args.get_deserialized()
        ca_kwargs = serialized_kwargs.get_deserialized()
        app_log.debug(f"Invoking ({ca_fn}, args={ca_args}, kwargs={ca_kwargs}")
        ca_fn(*ca_args, **ca_kwargs)

    return output
