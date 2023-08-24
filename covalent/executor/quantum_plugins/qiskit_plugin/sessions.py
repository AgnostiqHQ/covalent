# Copyright 2023 Agnostiq Inc.
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
Defines interactions with Qiskit Runtime sessions and services.
"""
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Union

from qiskit_ibm_runtime import QiskitRuntimeService, Session


@lru_cache
def init_runtime_service(
    *,
    ibmqx_token: str = None,
    ibmqx_url: str = None,
    channel: str = "",
    instance: str = "",
    cloud_instance: str = "",
    hub: str = "",
    group: str = "",
    project: str = "",
) -> QiskitRuntimeService:
    """
    Start `QiskitRuntimeService` with specified settings.
    """

    if channel == "ibm_quantum":
        if not instance:
            # Combine hub, group, and project to produce the instance.
            hgp = [hub, group, project]
            if all(hgp):
                instance = "/".join(hgp)
            else:
                instance = "ibm-q/open/main"

    elif channel == "ibm_cloud":
        # Require `cloud_instance` to be specified in this case.
        if not cloud_instance:
            raise ValueError("The `cloud_instance` is required for the 'ibm_cloud' channel.")

        instance = cloud_instance

    else:
        raise ValueError(
            "Invalid `channel` argument, must be either 'ibm_quantum' or 'ibm_cloud'."
        )

    # Initialize the runtime service instance.
    return QiskitRuntimeService(
        channel=channel, token=ibmqx_token, url=ibmqx_url, instance=instance
    )


@dataclass(frozen=True)
class SessionIdentifier:
    """
    Proxy for defining a unique `Session` instance.
    """

    service_channel: str
    service_instance: str
    service_url: str
    backend_name: str
    max_time: Union[int, None]


def get_cached_session(service, backend, max_time) -> Session:
    """
    Global Qiskit IBM Runtime sessions, unique up to fields in `SessionIdentifier`
    """
    session_id = make_session_id(service, backend, max_time)
    if session_id not in _sessions:
        _sessions[session_id] = Session(
            service=service,
            backend=backend,
            max_time=max_time,
        )

    return _sessions[session_id]


def make_session_id(service, backend, max_time) -> SessionIdentifier:
    """
    Create session identifier from `Session` initialization arguments
    """
    return SessionIdentifier(
        # pylint: disable=protected-access
        service_channel=service._account.channel,
        service_instance=service._account.instance,
        service_url=service._account.url,
        backend_name=backend.name,
        max_time=max_time,
    )


_sessions: Dict[SessionIdentifier, Session] = {}
