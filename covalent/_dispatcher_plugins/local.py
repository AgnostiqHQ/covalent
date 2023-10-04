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

import os
import tempfile
from copy import deepcopy
from functools import wraps
from pathlib import Path
from typing import Callable, List, Optional

import requests

from .._results_manager import wait
from .._results_manager.result import Result
from .._results_manager.results_manager import get_result
from .._serialize.result import merge_response_manifest, serialize_result, strip_local_uris
from .._shared_files import logger
from .._shared_files.config import get_config
from .._shared_files.schemas.asset import AssetSchema
from .._shared_files.schemas.result import ResultSchema
from .._shared_files.utils import copy_file_locally, format_server_url, request_api_key
from .._workflow.lattice import Lattice
from .base import BaseDispatcher

app_log = logger.app_log

dispatch_cache_dir = Path(get_config("sdk.dispatch_cache_dir"))
dispatch_cache_dir.mkdir(parents=True, exist_ok=True)


class AuthorizationError(Exception):
    pass


class AssetUploadFailed(Exception):
    pass


class LocalDispatcher(BaseDispatcher):
    """
    Local dispatcher which sends the workflow to the locally running
    dispatcher server.
    """

    @staticmethod
    def dispatch(
        orig_lattice: Lattice,
        dispatcher_addr: str = None,
        *,
        disable_run: bool = False,
    ) -> Callable:
        """
        Wrapping the dispatching functionality to allow input passing
        and server address specification.

        Afterwards, send the lattice to the dispatcher server and return
        the assigned dispatch id.

        Args:
            orig_lattice: The lattice/workflow to send to the dispatcher server.
            dispatcher_addr: The address of the dispatcher server.  If None then then defaults to the address set in Covalent's config.

        Returns:
            Wrapper function which takes the inputs of the workflow as arguments
        """

        multistage = get_config("sdk.multistage_dispatch") == "true"

        @wraps(orig_lattice)
        def wrapper(*args, **kwargs) -> str:
            """
            Send the lattice to the dispatcher server and return
            the assigned dispatch id.

            Args:
                *args: The inputs of the workflow.
                **kwargs: The keyword arguments of the workflow.

            Returns:
                The dispatch id of the workflow.
            """

            if multistage:
                dispatch_id = LocalDispatcher.register(orig_lattice, dispatcher_addr)(
                    *args, **kwargs
                )
            else:
                dispatch_id = LocalDispatcher.submit(orig_lattice, dispatcher_addr)(
                    *args, **kwargs
                )

            if not disable_run:
                return LocalDispatcher.start(dispatch_id, dispatcher_addr)
            else:
                return dispatch_id

        return wrapper

    @staticmethod
    def submit(
        orig_lattice: Lattice,
        dispatcher_addr: str = None,
    ) -> Callable:
        """
        Wrapping the dispatching functionality to allow input passing
        and server address specification.

        Afterwards, send the lattice to the dispatcher server and return
        the assigned dispatch id.

        Args:
            orig_lattice: The lattice/workflow to send to the dispatcher server.
            dispatcher_addr: The address of the dispatcher server.  If None then then defaults to the address set in Covalent's config.

        Returns:
            Wrapper function which takes the inputs of the workflow as arguments
        """

        if dispatcher_addr is None:
            dispatcher_addr = format_server_url()

        @wraps(orig_lattice)
        def wrapper(*args, **kwargs) -> str:
            """
            Send the lattice to the dispatcher server and return
            the assigned dispatch id.

            Args:
                *args: The inputs of the workflow.
                **kwargs: The keyword arguments of the workflow.

            Returns:
                The dispatch id of the workflow.
            """

            lattice = deepcopy(orig_lattice)

            lattice.build_graph(*args, **kwargs)

            # Serialize the transport graph to JSON
            json_lattice = lattice.serialize_to_json()

            test_url = f"{dispatcher_addr}/api/v1/dispatchv2/submit"
            headers = {"x-api-key": request_api_key()}

            if not headers["x-api-key"]:
                return

            r = requests.post(test_url, data=json_lattice, headers=headers)
            r.raise_for_status()
            return r.content.decode("utf-8").strip().replace('"', "")

        return wrapper

    @staticmethod
    def start(
        dispatch_id: str,
        dispatcher_addr: str = None,
    ) -> Callable:
        """
        Wrapping the dispatching functionality to allow input passing
        and server address specification.

        Afterwards, send the lattice to the dispatcher server and return
        the assigned dispatch id.

        Args:
            orig_lattice: The lattice/workflow to send to the dispatcher server.
            dispatcher_addr: The address of the dispatcher server.  If None then then defaults to the address set in Covalent's config.

        Returns:
            Wrapper function which takes the inputs of the workflow as arguments
        """

        if dispatcher_addr is None:
            dispatcher_addr = format_server_url()

        test_url = f"{dispatcher_addr}/api/v1/dispatchv2/start/{dispatch_id}"
        headers = {"x-api-key": request_api_key()}

        if not headers["x-api-key"]:
            return

        r = requests.put(test_url, headers=headers)
        r.raise_for_status()
        return r.content.decode("utf-8").strip().replace('"', "")

    @staticmethod
    def dispatch_sync(
        lattice: Lattice,
        dispatcher_addr: str = None,
    ) -> Callable:
        """
        Wrapping the synchronous dispatching functionality to allow input
        passing and server address specification.

        Afterwards, sends the lattice to the dispatcher server and return
        the result of the executed workflow.

        Args:
            orig_lattice: The lattice/workflow to send to the dispatcher server.
            dispatcher_addr: The address of the dispatcher server. If None then then defaults to the address set in Covalent's config.

        Returns:
            Wrapper function which takes the inputs of the workflow as arguments
        """

        if dispatcher_addr is None:
            dispatcher_addr = format_server_url()

        @wraps(lattice)
        def wrapper(*args, **kwargs) -> Result:
            """
            Send the lattice to the dispatcher server and return
            the result of the executed workflow.

            Args:
                *args: The inputs of the workflow.
                **kwargs: The keyword arguments of the workflow.

            Returns:
                The result of the executed workflow.
            """

            return get_result(
                LocalDispatcher.dispatch(lattice, dispatcher_addr)(*args, **kwargs),
                wait=wait.EXTREME,
            )

        return wrapper

    @staticmethod
    def register(
        orig_lattice: Lattice,
        dispatcher_addr: str = None,
    ) -> Callable:
        """
        Wrapping the dispatching functionality to allow input passing
        and server address specification.

        Afterwards, send the lattice to the dispatcher server and return
        the assigned dispatch id.

        Args:
            orig_lattice: The lattice/workflow to send to the dispatcher server.
            dispatcher_addr: The address of the dispatcher server.  If None then then defaults to the address set in Covalent's config.

        Returns:
            Wrapper function which takes the inputs of the workflow as arguments
        """

        if dispatcher_addr is None:
            dispatcher_addr = format_server_url()

        @wraps(orig_lattice)
        def wrapper(*args, **kwargs) -> str:
            """
            Send the lattice to the dispatcher server and return
            the assigned dispatch id.

            Args:
                *args: The inputs of the workflow.
                **kwargs: The keyword arguments of the workflow.

            Returns:
                The dispatch id of the workflow.
            """

            lattice = deepcopy(orig_lattice)

            lattice.build_graph(*args, **kwargs)

            with tempfile.TemporaryDirectory() as tmp_dir:
                manifest = LocalDispatcher.prepare_manifest(lattice, tmp_dir)
                LocalDispatcher.register_manifest(manifest, dispatcher_addr)

                dispatch_id = manifest.metadata.dispatch_id

                path = dispatch_cache_dir / f"{dispatch_id}"

                with open(path, "w") as f:
                    f.write(manifest.json())

                LocalDispatcher.upload_assets(manifest)

                return dispatch_id

        return wrapper

    @staticmethod
    def prepare_manifest(lattice, storage_path) -> ResultSchema:
        """Prepare a built-out lattice for submission"""

        result_object = Result(lattice)
        return serialize_result(result_object, storage_path)

    @staticmethod
    def register_manifest(
        manifest: ResultSchema,
        dispatcher_addr: Optional[str] = None,
        parent_dispatch_id: Optional[str] = None,
        push_assets: bool = True,
    ) -> ResultSchema:
        """Submits a manifest for registration.

        Returns:
            Dictionary representation of manifest with asset remote_uris filled in

        Side effect:
            If push_assets is False, the server will automatically pull the task assets from the submitted asset URIs.
        """

        if dispatcher_addr is None:
            dispatcher_addr = format_server_url()

        stripped = strip_local_uris(manifest) if push_assets else manifest
        register_dispatch_endpoint = f"{dispatcher_addr}/api/v2/lattices"

        headers = {"X-SESSION-TOKEN": os.getenv("COVALENT_JOB_SESSION_TOKEN")}

        if headers.get("X-SESSION-TOKEN") is None:
            raise AuthorizationError

        if parent_dispatch_id:
            register_dispatch_endpoint = (
                f"{register_dispatch_endpoint}/{parent_dispatch_id}/sublattices"
            )

        r = requests.post(register_dispatch_endpoint, data=stripped.json(), headers=headers)
        r.raise_for_status()

        parsed_resp = ResultSchema.parse_obj(r.json())

        return merge_response_manifest(manifest, parsed_resp)

    @staticmethod
    def upload_assets(manifest: ResultSchema):
        assets = LocalDispatcher._extract_assets(manifest)
        LocalDispatcher._upload(assets)

    @staticmethod
    def _extract_assets(manifest: ResultSchema) -> List[AssetSchema]:
        assets = []

        # workflow-level assets
        dispatch_assets = manifest.assets
        for key, asset in dispatch_assets:
            assets.append(asset)

        lattice = manifest.lattice
        lattice_assets = lattice.assets
        for key, asset in lattice_assets:
            assets.append(asset)

        # Node assets
        tg = lattice.transport_graph
        nodes = tg.nodes
        for node in nodes:
            node_assets = node.assets
            for key, asset in node_assets:
                assets.append(asset)
        return assets

    @staticmethod
    def _upload(assets: List[AssetSchema]):
        local_scheme_prefix = "file://"
        total = len(assets)
        for i, asset in enumerate(assets):
            if asset.remote_uri.startswith(local_scheme_prefix):
                copy_file_locally(asset.uri, asset.remote_uri)
            else:
                _upload_asset(asset.uri, asset.remote_uri)
            app_log.debug(f"uploaded {i+1} out of {total} assets.")


def _upload_asset(local_uri, remote_uri):
    scheme_prefix = "file://"
    if local_uri.startswith(scheme_prefix):
        local_path = local_uri[len(scheme_prefix) :]
    else:
        local_path = local_uri

    try:
        if os.path.getsize(local_path) == 0:
            r = requests.put(remote_uri, headers={"Content-Length": "0"}, data="")
        else:
            with open(local_path, "rb") as f:
                r = requests.put(remote_uri, data=f)
                r.raise_for_status()
    except Exception as err:
        raise AssetUploadFailed(f"Asset upload failed due to error: {err}") from err
