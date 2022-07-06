#!/usr/bin/env python3

import argparse
import os
import random
import shutil
import time
import types
from datetime import datetime
from pathlib import Path
from pprint import pprint

import cloudpickle as pickle
import networkx as nx
from sqlalchemy import inspect
from sqlalchemy.orm import Session

import covalent as ct
from covalent._data_store import DataStore
from covalent._data_store.models import Electron, ElectronDependency, Lattice
from covalent.executor import _executor_manager


@ct.electron
def task_1(x, y):
    return [x * y, x + y]


@ct.electron
def sublattice_task(z):
    return z


@ct.electron
@ct.lattice
def task_2(z):
    res = sublattice_task(z)
    return res


@ct.lattice
def attribute_workflow_1(a, b):
    res_1 = task_1(a, b)
    res_2 = task_2(res_1[1], b)
    return res_2


@ct.electron
def task_1(x, y):
    return {"key_1": x * y, "key_2": x + y}


@ct.electron
def sublattice_task(z):
    return z


@ct.electron
@ct.lattice
def task_2(z):
    res = sublattice_task(z)
    return res


@ct.lattice
def attribute_workflow_0(a, b):
    res_1 = task_1(a, b)
    res_2 = task_2(res_1["key_1"], b)
    return res_2


@ct.electron
def join_words(a, b):
    return ", ".join([a, b])


@ct.electron
def excitement(a):
    return f"{a}!"


@ct.electron
def makeint():
    return 1


@ct.lattice
def simple_workflow(a, b):
    time.sleep(5)
    phrase = join_words(a, b)
    return excitement(phrase)


@ct.lattice
def error_workflow(a):
    return excitement(a) + makeint()


@ct.lattice
def another_error(a, b):
    s = simple_workflow(a, b)
    return s * makeint()


@ct.electron
def add(a, b):
    time.sleep(10)
    return a + b


@ct.electron
def identity(a):
    return a


@ct.lattice
def check(a, b):
    result1 = add(a=a, b=b)
    return identity(a=result1)


@ct.lattice
def check_alt(a, b):
    time.sleep(10)
    result1 = add(a=a, b=b)
    return identity(a=result1)


@ct.electron
def collect(l_electrons):
    return l_electrons


@ct.lattice
def workflow():
    # Use keywords to specify parameters
    a_list = [identity(a=i) for i in range(5)]
    b_list = [identity(a=i) for i in range(5, 10)]
    return collect(l_electrons=[a_list, b_list])


@ct.electron
def new_func(a, b, c, d, e):
    time.sleep(10)
    return a + b + c + d + e


@ct.electron
@ct.lattice
def work_func(a, b, c):
    return new_func(a, b, c, d=4, e=5)


@ct.electron
def test_func(a, b):
    print(a)
    print(b)
    return a + b


@ct.lattice
def work_a(a, b):
    return test_func(a, b)


@ct.electron
def task(a, /, b, *args, c, **kwargs):
    return a * b * c, args, kwargs


@ct.electron
@ct.lattice
def workflow0():
    return task(1, 2, 3, 4, c=5, d=6, e=7)


@ct.electron
def say_hello():
    time.sleep(10)
    print("hello")
    return "hello"


@ct.electron
def say_all(a):
    for word in a:
        print(a)
    return a[:1]


@ct.lattice
def outputs(a, b, c):
    x = say_hello()
    y = say_all([a, b, c, say_hello(), "world"])
    return str(y) + x


@ct.lattice
def sublattice0(a):
    b = workflow0()
    c = say_hello()
    return str(b) + c + " " + a


@ct.lattice
def sublattice1(a, b):
    c = work_func(a, b, 1)
    d = test_func(a, b)
    return str(c) + b


workflows = [
    (attribute_workflow_0, (-1, 1)),
    (attribute_workflow_1, (-1, 1)),
    (sublattice0, ("world")),
    (sublattice1, ("hello", "world")),
    (simple_workflow, ("hello", "world")),
    (error_workflow, ("hello")),
    (another_error, ("another", "error")),
    (check, (1, 2)),
    (check_alt, (3, 4)),
    (check_alt, (ct.electron(check(0, 0)), 1)),
    (workflow, ()),
    (work_func, (5, 6, 7)),
    (work_a, ("covalent", 0)),
    (workflow0, ()),
    (outputs, (8, 9, 10)),
]


db = DataStore("sqlite+pysqlite:///results.db", initialize_db=True)
engine = db._get_engine()
insp = inspect(engine)
tables = insp.get_table_names()

electron_id = 0
edge_id = 0
lattice_id = 0
electrons = []
edges = []
lattices = []

for workflow in workflows:
    lattice_id = lattice_id + 1
    lattice, args = workflow
    dispatch_id = ct.dispatch(lattice)(*args)
    print("***DISPATCH***")
    print(dispatch_id)
    time.sleep(5)  # Change this number to see different statuses
    result = ct.get_result(dispatch_id)
    result.save()

    lattice = Lattice(
        id=lattice_id,
        dispatch_id=dispatch_id,
        name=lattice.__name__,
        status=str(result._status),
        storage_type="local",
        storage_path=f"./results/{dispatch_id}/",
        function_filename="function.pkl",
        function_string_filename="function_string.txt",
        executor_filename="executor.pkl",
        error_filename="error.log",
        inputs_filename="inputs.pkl",
        results_filename="result.pkl",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        started_at=result._start_time,
        completed_at=result._end_time,
    )

    lattices.append(lattice)

    with open(os.path.join(f"./results/{dispatch_id}/", "executor.pkl"), "wb") as f:
        f.write(
            pickle.dumps(_executor_manager.get_executor(result.lattice.get_metadata("executor")))
        )

    data = nx.readwrite.node_link_data(result.lattice.transport_graph._graph)
    nodes = data["nodes"]
    links = data["links"]
    pprint(nodes)
    pprint(links)
    for node in nodes:
        electron_id = electron_id + 1
        storage_path = f"./results/{dispatch_id}/node_{node['id']}/"
        os.mkdir(storage_path)
        with open(os.path.join(storage_path, "function.pkl"), "wb") as f:
            f.write(pickle.dumps(node["function"]))
        if "function_string" in node.keys():
            function_string_filename = "function_string.txt"
            with open(os.path.join(storage_path, function_string_filename), "w") as f:
                f.write(str(node["function_string"]))
        else:
            function_string_filename = None
        with open(os.path.join(storage_path, "executor.pkl"), "wb") as f:
            f.write(pickle.dumps(_executor_manager.get_executor(node["metadata"]["executor"])))
        with open(os.path.join(storage_path, "result.pkl"), "wb") as f:
            f.write(pickle.dumps(node["sublattice_result"]))
        with open(os.path.join(storage_path, "error.log"), "w") as f:
            f.write(str(node["error"]))
        with open(os.path.join(storage_path, "stdout.log"), "w") as f:
            f.write(str(node["stdout"]))
        with open(os.path.join(storage_path, "stderr.log"), "w") as f:
            f.write(str(node["stderr"]))
        with open(os.path.join(storage_path, "info.log"), "w") as f:
            f.write(str(None))
        if "value" in node.keys():
            value_filename = "value.pkl"
            with open(os.path.join(storage_path, value_filename), "wb") as f:
                f.write(pickle.dumps(node["value"]))
        else:
            value_filename = None
        nodename = node["name"]
        nodetype = None
        if nodename[0] == ":":
            nodetype = nodename.split(nodename[0])[1]
        else:
            nodetype = "electron"
        electron = Electron(
            id=electron_id,
            parent_lattice_id=lattice.id,
            transport_graph_node_id=node["id"],
            type=nodetype,
            name=nodename,
            status=str(node["status"]),
            storage_type="local",
            storage_path=storage_path,
            function_filename="function.pkl",
            function_string_filename=function_string_filename,
            executor_filename="executor.pkl",
            results_filename="result.pkl",
            value_filename=value_filename,
            #            key=
            #            attribute_name=
            stdout_filename="stdout.log",
            stderr_filename="stderr.log",
            info_filename="info.log",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            started_at=node["start_time"],
            completed_at=node["end_time"],
        )
        electrons.append(electron)

    for link in links:
        edge_id = edge_id + 1
        electron_deps = ElectronDependency(
            id=edge_id,
            electron_id=link.get("target"),
            parent_electron_id=link.get("source"),
            edge_name=link.get("edge_name"),
            parameter_type=link.get("param_type"),
            arg_index=link.get("arg_index"),
            created_at=datetime.now(),
        )
        edges.append(electron_deps)

with Session(engine) as session:
    session.add_all(lattices)
    session.add_all(electrons)
    session.add_all(edges)
    session.commit()

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--show-tables", action="store_true")
args = parser.parse_args()
if args.show_tables:
    import pandas as pd

    for table in tables:
        sql_table = pd.read_sql_table(table_name=table, con=engine)
        print(sql_table)
