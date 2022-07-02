#!/usr/bin/env python3

import argparse
import os
import random
import shutil
from datetime import datetime
from pathlib import Path
from pprint import pprint

import cloudpickle as pickle
import networkx as nx
from sqlalchemy import inspect
from sqlalchemy.orm import Session

import covalent as ct
from covalent._data_store import DataStore
from covalent._data_store.models import (
    Electron,
    ElectronDependency,
    ElectronTypeEnum,
    Lattice,
    ParameterTypeEnum,
)
from covalent.executor import _executor_manager


# Construct tasks as "electrons"
@ct.electron
def join_words(a, b):
    return ", ".join([a, b])


@ct.electron
def excitement(a):
    return f"{a}!"


# Construct a workflow of tasks
@ct.lattice
def simple_workflow(a, b):
    phrase = join_words(a, b)
    return excitement(phrase)


db = DataStore("sqlite+pysqlite:///results.db", initialize_db=True)
engine = db._get_engine()
insp = inspect(engine)
tables = insp.get_table_names()
dispatch_id = ct.dispatch(simple_workflow)("Hello", "World")
result = ct.get_result(dispatch_id)
result.save()

electron_id = 0
edge_id = 0
lattice_id = 0
electrons = []
edges = []
lattices = []
print(result.lattice.transport_graph.get_topologically_sorted_graph())
print(result.lattice.transport_graph.get_node_value(2, "function").get_deserialized())
print(result.lattice.__name__)
print(result.lattice.workflow_function)
print(result.lattice.workflow_function_string)
print(result.lattice.get_metadata("executor"))
print(_executor_manager.get_executor(result.lattice.get_metadata("executor")))
print("error")
print(result.error)


print(dispatch_id)

lattice_id = lattice_id + 1

lattice = Lattice(
    id=lattice_id,
    dispatch_id=dispatch_id,
    name=simple_workflow.__name__,
    status=str(result._status),
    storage_type="local",
    storage_path=f"./results/{dispatch_id}/",
    function_filename="function.pkl",  # done
    function_string_filename="function_string.txt",  # done
    executor_filename="executor.pkl",  # done
    error_filename="error.log",  # done, TODO: make a lattice that causes an error
    inputs_filename="inputs.pkl",  # done
    results_filename="result.pkl",  # done
    created_at=datetime.now(),
    updated_at=datetime.now(),
    started_at=result._start_time,
    completed_at=result._end_time,
)

lattices.append(lattice)

with open(os.path.join(f"./results/{dispatch_id}/", "executor.pkl"), "wb") as f:
    f.write(pickle.dumps(_executor_manager.get_executor(result.lattice.get_metadata("executor"))))

data = nx.readwrite.node_link_data(result.lattice.transport_graph._graph)
nodes = data(["nodes"])
links = data(["links"])

for node in nodes:
    electron_id = electron_id + 1
    storage_path = f"./results/{dispatch_id}/node_{node.id}/"
    with open(os.path.join(storage_path, "function.pkl"), "wb") as f:
        f.write(pickle.dumps(node.function))
    with open(os.path.join(storage_path, "function_string.txt"), "w") as f:
        f.write(str(node.function_string))
    with open(os.path.join(storage_path, "executor.pkl"), "wb") as f:
        f.write(pickle.dumps(_executor_manager.get_executor(node.metadata.executor)))
    with open(os.path.join(storage_path, "result.pkl"), "wb") as f:
        f.write(pickle.dumps(node.sublattice_result))
    with open(os.path.join(storage_path, "error.log"), "w") as f:
        f.write(str(node.error))
    if "value" in node.keys():
        value_filename = "value.pkl"
        with open(os.path.join(storage_path, value_filename), "wb") as f:
            f.write(pickle.dumps(node.value))
    electron = Electron(
        id=electron_id,
        parent_lattice_id=lattice.id,
        transport_graph_node_id=node.id,
        type=ElectronTypeEnum.electron,
        name=node.name,
        status=str(node.status),
        storage_type="local",
        storage_path=storage_path,
        function_filename="function.pkl",
        function_string_filename="function_string.txt",
        executor_filename="executor.pkl",
        error_filename="error.log",
        results_filename="result.pkl",
        value_filename="value.pkl",
        stdout_filename="stdout.log",
        stderr_filename="stderr.log",
        info_filename="info.log",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        started_at=node.start_time,
        completed_at=node.end_time,
    )


electron_deps = ElectronDependency(
    id=1,
    electron_id=electron.id,
    parent_electron_id=2,
    edge_name="arg[0]",
    parameter_type=ParameterTypeEnum.NULL,
    arg_index=0,
    created_at=datetime.now(),
)

with Session(engine) as session:
    session.add(lattice)
    session.add(electron)
    session.add(electron_deps)
    session.commit()

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--show-tables", action="store_true")
args = parser.parse_args()
if args.show_tables:
    import pandas as pd

    for table in tables:
        sql_table = pd.read_sql_table(table_name=table, con=engine)
        print(sql_table)
