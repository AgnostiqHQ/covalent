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

"""Module containing post-processing related functions."""

from builtins import list
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Dict, List, Set, Union

from .._shared_files import logger
from .._shared_files.context_managers import active_lattice_manager
from .._shared_files.defaults import (
    DefaultMetadataValues,
    postprocess_prefix,
    prefix_separator,
    sublattice_prefix,
)
from .transport import _TransportGraph, encode_metadata

if TYPE_CHECKING:
    from .electron import Electron

DEFAULT_METADATA_VALUES = asdict(DefaultMetadataValues())

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class Postprocessor:
    def __init__(self, lattice) -> None:
        self.lattice = lattice

    def _is_postprocessable_node(self, tg: _TransportGraph, node_id: int) -> bool:
        """Filter nodes that should be included in postprocessing.

        Args:
            tg: Transport graph of the lattice.
            node_id: Node id of the node to be checked.

        Returns:
            True if the node should be included in postprocessing, False otherwise.

        """
        node_name = tg.get_node_value(node_id, "name")
        return bool(
            not node_name.startswith(prefix_separator) or node_name.startswith(sublattice_prefix)
        )

    def _filter_electrons(self, tg: _TransportGraph, bound_electrons: List) -> List:
        """Filter bound electrons for ones that should not be included in postprocessing.

        Args:
            tg: Transport graph of the lattice.
            bound_electrons: List of bound electrons.

        Returns:
            List of bound electrons that should be included in postprocessing.

        """
        filtered_node_ids = [
            node_id for node_id in tg._graph.nodes if self._is_postprocessable_node(tg, node_id)
        ]
        return [bound_electrons[node_id] for node_id in filtered_node_ids]

    def _postprocess(self, *ordered_node_outputs: List[Any]) -> Any:
        """
        Post processing function to be called after the lattice execution.
        This takes care of executing statements that were not an electron
        but were inside the lattice's function. It also replaces any calls
        to an electron with the result of that electron execution, hence
        preventing a local execution of electron's function.
        Note: Here `node_outputs` is used instead of `electron_outputs`
        since an electron can be called multiple times with possibly different
        arguments, but every time it's called, it will be executed as a separate node.
        Thus, output of every node is used.

        Args:
            ordered_node_outputs: List of outputs of every node in the lattice.

        Returns:
            result: The result of the lattice function.

        """
        with active_lattice_manager.claim(self.lattice):
            self.lattice.post_processing = True
            self.lattice.electron_outputs = list(ordered_node_outputs)
            args = [arg.get_deserialized() for arg in self.lattice.args]
            kwargs = {k: v.get_deserialized() for k, v in self.lattice.kwargs.items()}
            workflow_function = self.lattice.workflow_function.get_deserialized()
            result = workflow_function(*args, **kwargs)
            self.lattice.post_processing = False
            return result

    def _get_node_ids_from_retval(self, retval: Union["Electron", List, Dict]) -> Set[int]:
        """Get the list of electron node ids from the return value of a lattice function.

        Args:
            retval: Return value of a lattice function.

        Returns:
            List of electron node ids.

        """
        from .electron import Electron

        node_ids = []
        if isinstance(retval, Electron):
            node_ids.append(retval.node_id)
            app_log.debug(f"Preprocess: Encountered node {retval.node_id}")
        elif isinstance(retval, (list, tuple, set)):
            app_log.debug("Recursively preprocessing iterable")
            for e in retval:
                node_ids.extend(self._get_node_ids_from_retval(e))
        elif isinstance(retval, dict):
            app_log.debug("Recursively preprocessing dictionary")
            for _, v in retval.items():
                node_ids.extend(self._get_node_ids_from_retval(v))
        else:
            app_log.debug(f"Encountered primitive or unsupported type: {retval}")
            return []

        return set(node_ids)

    def _get_electron_metadata(self) -> Dict:
        """Get the metadata for the postprocess electron.

        Returns:
            Dictionary of metadata for the postprocess electron.

        """
        executor = self.lattice.get_metadata("workflow_executor")
        executor_data = self.lattice.get_metadata("workflow_executor_data")
        pp_metadata = encode_metadata(DEFAULT_METADATA_VALUES.copy())
        pp_metadata["executor"] = executor
        pp_metadata["executor_data"] = executor_data
        pp_metadata = encode_metadata(pp_metadata)
        return pp_metadata

    def add_exhaustive_postprocess_node(self, bound_electrons: Dict) -> None:
        """This function adds a postprocess node to the transport graph based on the 'exhaustive' algorithm.

        Args:
            bound_electrons: Dictionary of bound electrons with node_id as key and the electron object as the value. A bound is an electron that has been assigned a node_id and is part of a transport graph.

        Returns:
            None

        """
        from .electron import Electron

        with active_lattice_manager.claim(self.lattice):
            tg = self.lattice.transport_graph
            filtered_ordered_electrons = self._filter_electrons(tg, bound_electrons)
            pp_electron = Electron(
                function=self._postprocess, metadata=self._get_electron_metadata()
            )
            bound_pp = pp_electron(*filtered_ordered_electrons)
            tg.set_node_value(bound_pp.node_id, "name", postprocess_prefix)

    def _postprocess_recursively(self, retval, **referenced_outputs):
        from .electron import Electron

        if isinstance(retval, Electron):
            key = f"node:{retval.node_id}"
            return referenced_outputs[key]
        elif isinstance(retval, list):
            return list(
                map(lambda x: self._postprocess_recursively(x, **referenced_outputs), retval)
            )
        elif isinstance(retval, tuple):
            return tuple(
                map(lambda x: self._postprocess_recursively(x, **referenced_outputs), retval)
            )
        elif isinstance(retval, set):
            return {self._postprocess_recursively(x, **referenced_outputs) for x in retval}
        elif isinstance(retval, dict):
            return {
                k: self._postprocess_recursively(v, **referenced_outputs)
                for k, v in retval.items()
            }
        else:
            return retval

    def add_reconstruct_postprocess_node(
        self, retval: Union["Electron", List, Dict], bound_electrons: Dict
    ):
        """This function adds a postprocess node to the transport graph based on the 'eager reconstruction' algorithm.

        Args:
            retval: Return value of the lattice function.
            bound_electrons: Dictionary of bound electrons with node_id as key and the electron object as the value. A bound is an electron that has been assigned a node_id and is part of a transport graph.

        Returns:
            None

        """
        from .electron import Electron, wait

        node_id_refs = self._get_node_ids_from_retval(retval)
        referenced_electrons = {}
        for node_id in node_id_refs:
            key = f"node:{node_id}"
            referenced_electrons[key] = bound_electrons[node_id]

        with active_lattice_manager.claim(self.lattice):
            pp_metadata = self._get_electron_metadata()
            pp_electron = Electron(function=self._postprocess_recursively, metadata=pp_metadata)

            # Add pp_electron to the graph -- this will also add a
            # parameter node in case retval is not a single electron
            bound_pp = pp_electron(retval, **referenced_electrons)

            # Edit pp electron name
            self.lattice.transport_graph.set_node_value(
                bound_pp.node_id, "name", f"{postprocess_prefix}reconstruct"
            )

            # Wait for non-referenced electrons
            wait_parents = [v for k, v in bound_electrons.items() if k not in node_id_refs]
            wait(child=bound_pp, parents=wait_parents)
