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

import json
import os
from datetime import datetime

import cloudpickle
from sqlalchemy.orm import Session

from covalent_ui.api.v1.database.schema.electron import Electron
from covalent_ui.api.v1.database.schema.electron_dependency import ElectronDependency
from covalent_ui.api.v1.database.schema.lattices import Lattice
from tests.covalent_ui_backend_tests.utils.data.mock_files import mock_files_data

log_output_data = mock_files_data()


def seed(engine):
    lattice_records = []
    electron_records = []
    electron_dependency_records = []
    with open(
        "tests/covalent_ui_backend_tests/utils/data/lattices.json", "r", encoding="utf-8"
    ) as json_file:
        lattice_data = json.load(json_file)
        for item in lattice_data:
            lattice_records.append(
                Lattice(
                    id=item["id"],
                    dispatch_id=item["dispatch_id"],
                    electron_id=item["electron_id"],
                    name=item["name"],
                    status=item["status"],
                    electron_num=item["electron_num"],
                    completed_electron_num=item["completed_electron_num"],
                    docstring_filename=item["docstring_filename"],
                    deps_filename=item["deps_filename"],
                    call_before_filename=item["call_before_filename"],
                    call_after_filename=item["call_after_filename"],
                    cova_imports_filename=item["cova_imports_filename"],
                    lattice_imports_filename=item["lattice_imports_filename"],
                    storage_type=item["storage_type"],
                    storage_path=os.path.dirname(__file__)
                    + "/mock_files/"
                    + item["dispatch_id"],  # item["storage_path"],
                    function_filename=item["function_filename"],
                    function_string_filename=item["function_string_filename"],
                    executor=item["executor"],
                    executor_data_filename=item["executor_data_filename"],
                    workflow_executor=item["workflow_executor"],
                    workflow_executor_data_filename=item["workflow_executor_data_filename"],
                    error_filename=item["error_filename"],
                    inputs_filename=item["inputs_filename"],
                    named_args_filename=item["named_args_filename"],
                    named_kwargs_filename=item["named_kwargs_filename"],
                    results_filename=item["results_filename"],
                    transport_graph_filename=item["transport_graph_filename"],
                    root_dispatch_id=item["root_dispatch_id"],
                    is_active=item["is_active"],
                    created_at=convert_to_date(item["created_at"]),
                    updated_at=convert_to_date(item["updated_at"]),
                    started_at=convert_to_date(item["started_at"]),
                    completed_at=convert_to_date(item["completed_at"]),
                )
            )

    with open(
        "tests/covalent_ui_backend_tests/utils/data/electrons.json", "r", encoding="utf-8"
    ) as json_file:
        electron_data = json.load(json_file)
        for item in electron_data:
            electron_records.append(
                Electron(
                    id=item["id"],
                    parent_lattice_id=item["parent_lattice_id"],
                    transport_graph_node_id=item["transport_graph_node_id"],
                    type=item["type"],
                    name=item["name"],
                    status=item["status"],
                    storage_type=item["storage_type"],
                    storage_path=os.path.dirname(__file__)
                    + "/mock_files/"
                    + lattice_records[item["parent_lattice_id"] - 1].dispatch_id
                    + "/"
                    + "node_"
                    + str(item["transport_graph_node_id"]),
                    function_filename=item["function_filename"],
                    function_string_filename=item["function_string_filename"],
                    executor=item["executor"],
                    executor_data_filename=item["executor_data_filename"],
                    results_filename=item["results_filename"],
                    value_filename=item["value_filename"],
                    stdout_filename=item["stdout_filename"],
                    deps_filename=item["deps_filename"],
                    call_before_filename=item["call_before_filename"],
                    call_after_filename=item["call_after_filename"],
                    stderr_filename=item["stderr_filename"],
                    error_filename=item["info_filename"],
                    is_active=item["is_active"],
                    created_at=convert_to_date(item["created_at"]),
                    updated_at=convert_to_date(item["updated_at"]),
                    started_at=convert_to_date(item["started_at"]),
                    completed_at=convert_to_date(item["completed_at"]),
                )
            )

    with open(
        "tests/covalent_ui_backend_tests/utils/data/electron_dependency.json",
        "r",
        encoding="utf-8",
    ) as json_file:
        electron_dependency_data = json.load(json_file)
        for item in electron_dependency_data:
            electron_dependency_records.append(
                ElectronDependency(
                    id=item["id"],
                    electron_id=item["electron_id"],
                    parent_electron_id=item["parent_electron_id"],
                    edge_name=item["edge_name"],
                    parameter_type=item["parameter_type"],
                    arg_index=item["arg_index"],
                    is_active=item["is_active"],
                    updated_at=convert_to_date(item["updated_at"]),
                    created_at=convert_to_date(item["created_at"]),
                )
            )
    with Session(engine) as session:
        session.bulk_save_objects(lattice_records)
        session.bulk_save_objects(electron_records)
        session.bulk_save_objects(electron_dependency_records)
        session.commit()


def seed_files():
    """Seed Log Files"""
    for section_key, _ in log_output_data.items():
        logs_section = log_output_data[section_key]
        log_dir = logs_section["path"]
        dir_exists = os.path.exists(log_dir)
        if not dir_exists:
            os.makedirs(log_dir)
        for file in logs_section["files"]:
            log_file_path = f"{log_dir}/{file['file_name']}"
            if file["file_name"].endswith(".pkl"):
                with open(log_file_path, "wb") as log_file:
                    cloudpickle.dump(file["data"], log_file)
            else:
                with open(log_file_path, "w") as log_file:
                    log_file.write(file["data"])


def convert_to_date(date_str: str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
