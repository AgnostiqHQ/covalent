import json
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from covalent_ui.api.v1.database.schema.electron import Electron
from covalent_ui.api.v1.database.schema.electron_dependency import ElectronDependency
from covalent_ui.api.v1.database.schema.lattices import Lattice


def seed(engine):
    lattice_records = []
    electron_records = []
    electron_dependency_records = []
    with open("tests/ui_backend_tests/utils/data/lattice.json") as json_file:
        lattice_data = json.load(json_file)
        for item in lattice_data["lattice"]:
            lattice_records.append(
                Lattice(
                    id=item["id"],
                    dispatch_id=item["dispatch_id"],
                    electron_id=item["electron_id"],
                    name=item["name"],
                    status=item["status"],
                    electron_num=item["electron_num"],
                    completed_electron_num=item["completed_electron_num"],
                    storage_type=item["storage_type"],
                    storage_path=item["storage_path"],
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
                    is_active=item["is_active"],
                    created_at=convert_to_date(item["created_at"]),
                    updated_at=convert_to_date(item["updated_at"]),
                    started_at=convert_to_date(item["started_at"]),
                    completed_at=convert_to_date(item["completed_at"]),
                )
            )
    with open("tests/ui_backend_tests/utils/data/electrons.json") as json_file:
        electron_data = json.load(json_file)
        for item in electron_data["electrons"]:
            electron_records.append(
                Electron(
                    id=item["id"],
                    parent_lattice_id=item["parent_lattice_id"],
                    transport_graph_node_id=item["transport_graph_node_id"],
                    type=item["type"],
                    name=item["name"],
                    status=item["status"],
                    storage_type=item["storage_type"],
                    storage_path=item["storage_path"],
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
                    info_filename=item["info_filename"],
                    is_active=item["is_active"],
                    created_at=convert_to_date(item["created_at"]),
                    updated_at=convert_to_date(item["updated_at"]),
                    started_at=convert_to_date(item["started_at"]),
                    completed_at=convert_to_date(item["completed_at"]),
                )
            )
    with open("tests/ui_backend_tests/utils/data/electron_dependency.json") as json_file:
        electron_dependency_data = json.load(json_file)
        for item in electron_dependency_data["electron_dependency"]:
            electron_dependency_records.append(
                ElectronDependency(
                    id=item["id"],
                    electron_id=item["electron_id"],
                    parent_electron_id=item["electron_id"],
                    edge_name=item["electron_id"],
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


def convert_to_date(date_str: str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
