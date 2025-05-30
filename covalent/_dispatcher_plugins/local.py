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

import base64
import os
import tarfile
import tempfile
from copy import deepcopy
from functools import wraps
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

from .._api.apiclient import CovalentAPIClient as APIClient
from .._file_transfer import FileTransfer
from .._results_manager.result import Result
from .._results_manager.results_manager import get_result, get_result_manager
from .._serialize.result import (
    extract_assets,
    merge_response_manifest,
    serialize_result,
    strip_local_uris,
)
from .._shared_files import logger
from .._shared_files.config import get_config
from .._shared_files.schemas.asset import AssetSchema
from .._shared_files.schemas.result import ResultSchema
from .._shared_files.utils import format_server_url
from .._workflow.lattice import Lattice
from ..triggers import BaseTrigger
from .base import BaseDispatcher

app_log = logger.app_log
log_stack_info = logger.log_stack_info

dispatch_cache_dir = Path(get_config("sdk.dispatch_cache_dir"))
dispatch_cache_dir.mkdir(parents=True, exist_ok=True)


BASE_ENDPOINT = os.getenv("COVALENT_DISPATCH_BASE_ENDPOINT", "/api/v2/dispatches")


def get_redispatch_request_body_v2(
    dispatch_id: str,
    staging_dir: str,
    new_args: List,
    new_kwargs: Dict,
    replace_electrons: Optional[Dict[str, Callable]],
    dispatcher_addr: str = None,
) -> ResultSchema:
    rm = get_result_manager(dispatch_id, dispatcher_addr=dispatcher_addr, wait=True)
    manifest = ResultSchema.model_validate(rm._manifest)

    # If no changes to inputs or electron, just retry the dispatch
    if not new_args and not new_kwargs and not replace_electrons:
        manifest.reset_metadata()
        app_log.debug("Resubmitting manifest only")
        return manifest

    # In all other cases we need to rebuild the graph
    rm.download_lattice_asset("workflow_function")
    rm.download_lattice_asset("workflow_function_string")
    rm.load_lattice_asset("workflow_function")
    rm.load_lattice_asset("workflow_function_string")

    if replace_electrons is None:
        replace_electrons = {}

    lat = rm.result_object.lattice

    if replace_electrons:
        lat._replace_electrons = replace_electrons

    # If lattice inputs are not supplied, retrieve them from the previous dispatch
    if not new_args and not new_kwargs:
        rm.download_lattice_asset("inputs")
        rm.load_lattice_asset("inputs")
        res_obj = rm.result_object
        inputs = res_obj.inputs.get_deserialized()
        new_args = inputs["args"]
        new_kargs = inputs["kwargs"]

    lat.build_graph(*new_args, **new_kwargs)
    if replace_electrons:
        del lat.__dict__["_replace_electrons"]

    return serialize_result(Result(lat), staging_dir)


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
            dispatcher_addr: The address of the dispatcher server. If None then defaults to the address set in Covalent's config.

        Kwargs:
            disable_run: Whether to disable running the workflow and rather just save it on Covalent's server for later execution.

        Returns:
            Wrapper function which takes the inputs of the workflow as arguments
        """

        # Extract triggers here
        if "triggers" in orig_lattice.metadata:
            triggers_data = orig_lattice.metadata.pop("triggers")
        else:
            triggers_data = None

        if not disable_run:
            # Determine whether to disable first run based on trigger_data
            disable_run = triggers_data is not None

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

            dispatch_id = LocalDispatcher.register(orig_lattice, dispatcher_addr)(*args, **kwargs)

            if triggers_data:
                LocalDispatcher.register_triggers(triggers_data, dispatch_id)

            if not disable_run:
                return LocalDispatcher.start(dispatch_id, dispatcher_addr)
            else:
                return dispatch_id

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

            if not isinstance(orig_lattice, Lattice):
                message = f"Dispatcher expected a Lattice, received {type(orig_lattice)} instead."
                app_log.error(message)
                raise TypeError(message)

            lattice = deepcopy(orig_lattice)

            lattice.build_graph(*args, **kwargs)

            with tempfile.TemporaryDirectory() as tmp_dir:
                manifest = LocalDispatcher.prepare_manifest(lattice, tmp_dir)
                LocalDispatcher.register_manifest(manifest, dispatcher_addr)

                dispatch_id = manifest.metadata.dispatch_id

                path = dispatch_cache_dir / f"{dispatch_id}"

                with open(path, "w") as f:
                    f.write(manifest.model_dump_json())

                LocalDispatcher.upload_assets(manifest)

                return dispatch_id

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

        endpoint = f"{BASE_ENDPOINT}/{dispatch_id}/status"
        body = {"status": "RUNNING"}
        r = APIClient(dispatcher_addr).put(endpoint, json=body)
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
            dispatcher_addr: The address of the dispatcher server. If None then defaults to the address set in Covalent's config.

        Returns:
            Wrapper function which takes the inputs of the workflow as arguments.
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
                wait=True,
            )

        return wrapper

    @staticmethod
    def redispatch(
        dispatch_id: str,
        dispatcher_addr: str = None,
        replace_electrons: Dict[str, Callable] = None,
        reuse_previous_results: bool = False,
    ) -> Callable:
        """
        Wrapping the dispatching functionality to allow input passing and server address specification.

        Args:
            dispatch_id: The dispatch id of the workflow to re-dispatch.
            dispatcher_addr: The address of the dispatcher server. If None then defaults to the address set in Covalent's config.
            replace_electrons: A dictionary of electron names and the new electron to replace them with.
            reuse_previous_results: Boolean value whether to reuse the results from the previous dispatch.

        Returns:
            Wrapper function which takes the inputs of the workflow as arguments.
        """

        if dispatcher_addr is None:
            dispatcher_addr = format_server_url()

        if replace_electrons is None:
            replace_electrons = {}

        return LocalDispatcher.register_redispatch(
            dispatch_id=dispatch_id,
            dispatcher_addr=dispatcher_addr,
            replace_electrons=replace_electrons,
            reuse_previous_results=reuse_previous_results,
        )

    @staticmethod
    def register_triggers(triggers_data: List[Dict], dispatch_id: str) -> None:
        """
        Register the given triggers to the Triggers server.
        Register also starts the `observe()` method of said trigger.
        This is done by calling `BaseTrigger._register` method
        with the given trigger dictionary and is equivalent to
        calling the trigger objects `register()` method.

        Args:
            triggers_data: List of trigger dictionaries to be registered
            dispatch_id: Lattice's dispatch id to be linked with given triggers

        Returns:
            None
        """

        for tr_dict in triggers_data:
            tr_dict["lattice_dispatch_id"] = dispatch_id
            BaseTrigger._register(tr_dict)

    @staticmethod
    def stop_triggers(
        dispatch_ids: Union[str, List[str]], triggers_server_addr: str = None
    ) -> None:
        """
        Stop observing on all triggers of all given dispatch ids registered on the Triggers server.
        Args:
            dispatch_ids: Dispatch ID(s) for whose triggers are to be stopped
            triggers_server_addr: Address of the Triggers server; configured dispatcher's address is used as default
        Returns:
            None
        """

        if triggers_server_addr is None:
            triggers_server_addr = (
                "http://"
                + get_config("dispatcher.address")
                + ":"
                + str(get_config("dispatcher.port"))
            )

        if isinstance(dispatch_ids, str):
            dispatch_ids = [dispatch_ids]

        endpoint = "/api/triggers/stop_observe"
        r = APIClient(triggers_server_addr).post(endpoint, json=dispatch_ids)
        r.raise_for_status()

        app_log.debug("Triggers for following dispatch_ids have stopped observing:")
        for d_id in dispatch_ids:
            app_log.debug(d_id)

    @staticmethod
    def register_redispatch(
        dispatch_id: str,
        dispatcher_addr: str = None,
        replace_electrons: Dict[str, Callable] = None,
        reuse_previous_results: bool = False,
    ) -> Callable:
        """
        Wrapping the dispatching functionality to allow input passing and server address specification.

        Args:
            dispatch_id: The dispatch id of the workflow to re-dispatch.
            dispatcher_addr: The address of the dispatcher server. If None then defaults to the address set in Covalent's config.
            replace_electrons: A dictionary of electron names and the new electron to replace them with.
            reuse_previous_results: Boolean value whether to reuse the results from the previous dispatch.

        Returns:
            Wrapper function which takes the inputs of the workflow as arguments.
        """

        if dispatcher_addr is None:
            dispatcher_addr = format_server_url()

        def func(*new_args, **new_kwargs):
            """
            Prepare the redispatch request body and redispatch the workflow.

            Args:
                *args: The inputs of the workflow.
                **kwargs: The keyword arguments of the workflow.

            Returns:
                The result of the executed workflow.
            """

            with tempfile.TemporaryDirectory() as staging_dir:
                manifest = get_redispatch_request_body_v2(
                    dispatch_id=dispatch_id,
                    staging_dir=staging_dir,
                    new_args=new_args,
                    new_kwargs=new_kwargs,
                    replace_electrons=replace_electrons,
                    dispatcher_addr=dispatcher_addr,
                )

                LocalDispatcher.register_derived_manifest(
                    manifest,
                    dispatch_id,
                    reuse_previous_results=reuse_previous_results,
                    dispatcher_addr=dispatcher_addr,
                )

                redispatch_id = manifest.metadata.dispatch_id

                path = dispatch_cache_dir / f"{redispatch_id}"

                with open(path, "w") as f:
                    f.write(manifest.model_dump_json())

                LocalDispatcher.upload_assets(manifest)

            return LocalDispatcher.start(redispatch_id, dispatcher_addr)

        return func

    @staticmethod
    def prepare_manifest(lattice, storage_path) -> ResultSchema:
        """Prepare a built-out lattice for submission"""

        result_object = Result(lattice)
        return serialize_result(result_object, storage_path)

    @staticmethod
    def register_manifest(
        manifest: ResultSchema,
        dispatcher_addr: Optional[str] = None,
        push_assets: bool = True,
    ) -> ResultSchema:
        """Submits a manifest for registration.

        Returns:
            Dictionary representation of manifest with asset remote_uris filled in

        Side effect:
            If push_assets is False, the server will
            automatically pull the task assets from the submitted asset URIs.
        """

        if dispatcher_addr is None:
            dispatcher_addr = format_server_url()

        stripped = strip_local_uris(manifest) if push_assets else manifest
        endpoint = BASE_ENDPOINT

        r = APIClient(dispatcher_addr).post(endpoint, data=stripped.model_dump_json())
        r.raise_for_status()

        parsed_resp = ResultSchema.model_validate(r.json())

        return merge_response_manifest(manifest, parsed_resp)

    @staticmethod
    def register_derived_manifest(
        manifest: ResultSchema,
        dispatch_id: str,
        reuse_previous_results: bool = False,
        dispatcher_addr: Optional[str] = None,
    ) -> ResultSchema:
        """Submits a derived manifest for registration.

        Returns:
            Dictionary representation of manifest with asset remote_uris filled in

        """

        if dispatcher_addr is None:
            dispatcher_addr = format_server_url()

        # We don't yet support pulling assets for redispatch
        stripped = strip_local_uris(manifest)

        endpoint = f"{BASE_ENDPOINT}/{dispatch_id}/redispatches"

        params = {"reuse_previous_results": reuse_previous_results}
        r = APIClient(dispatcher_addr).post(
            endpoint, data=stripped.model_dump_json(), params=params
        )
        r.raise_for_status()

        parsed_resp = ResultSchema.model_validate(r.json())

        return merge_response_manifest(manifest, parsed_resp)

    @staticmethod
    def upload_assets(manifest: ResultSchema):
        assets = extract_assets(manifest)
        LocalDispatcher._upload(assets)

    @staticmethod
    def _upload(assets: List[AssetSchema]):
        total = len(assets)
        number_uploaded = 0
        for i, asset in enumerate(assets):
            if not asset.remote_uri or not asset.uri:
                app_log.debug(f"Skipping asset {i + 1} out of {total}")
                continue

            _upload_asset(asset.uri, asset.remote_uri)
            number_uploaded += 1
        app_log.debug(f"Uploaded asset {i + 1} out of {total}.")
        app_log.debug(f"uploaded {number_uploaded} assets.")


def _upload_asset(local_uri, remote_uri):
    _, ft = FileTransfer(local_uri, remote_uri).cp()
    ft()


# Archive staging directory and manifest
# Used for sublattice dispatch when the executor cannot directly
# submit the sublattice to the control plane
def pack_staging_dir(staging_dir, manifest: ResultSchema) -> str:
    # save manifest json to staging root
    with open(os.path.join(staging_dir, "manifest.json"), "w") as f:
        f.write(manifest.model_dump_json())

    # Tar up staging dir
    with tempfile.NamedTemporaryFile(suffix=".tar") as f:
        tar_path = f.name

    with tarfile.TarFile(tar_path, "w") as tar:
        tar.add(staging_dir, recursive=True)
    return tar_path


# Inverse of `pack_staging_dir`
# Consumed by server-side tarball importer
def untar_staging_dir(tar_name) -> Tuple[str, ResultSchema]:

    # Working directory for unpacking the archive
    with tempfile.TemporaryDirectory(prefix="postprocess-") as work_dir:
        ...

    # Find and extract manifest
    with tarfile.TarFile(tar_name) as tar:
        manifest_path = list(filter(lambda x: x.endswith("manifest.json"), tar.getnames()))
        if len(manifest_path) == 0:
            raise RuntimeError("Archive contains no manifest")

        manifest = ResultSchema.model_validate_json(tar.extractfile(manifest_path[0]).read())

        tar.extractall(path=work_dir, filter="tar")

    # prepend work_dir to each asset path
    scheme_prefix = "file://"
    for _, asset in manifest.assets:
        if asset.uri:
            path = asset.uri[len(scheme_prefix) :]
            asset.uri = f"{scheme_prefix}{work_dir}{path}"
            print("Rewrote asset uri ", asset.uri)
    for _, asset in manifest.lattice.assets:
        if asset.uri:
            path = asset.uri[len(scheme_prefix) :]
            asset.uri = f"{scheme_prefix}{work_dir}{path}"
            print("Rewrote asset uri ", asset.uri)

    for node in manifest.lattice.transport_graph.nodes:
        for _, asset in node.assets:
            if asset.uri:
                path = asset.uri[len(scheme_prefix) :]
                asset.uri = f"{scheme_prefix}{work_dir}{path}"
                print("Rewrote asset uri ", asset.uri)

    return work_dir, manifest


# Consumed by server-side tarball importer (`import_b64_staging_tarball`)
# TODO: support streaming decode to avoid having to load the entire buffer in mem
def decode_b64_tar(b64_buffer: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".tar") as tar_file:
        tar_path = tar_file.name

    with open(tar_path, "wb") as tar_file:
        tar_file.write(base64.b64decode(b64_buffer.encode("utf-8")))

    return tar_path
