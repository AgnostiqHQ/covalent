#!/usr/bin/env python3

import argparse
from datetime import datetime

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


db = DataStore("sqlite+pysqlite:///", initialize_db=True)
engine = db._get_engine()
insp = inspect(engine)
tables = insp.get_table_names()
dispatch_id = ct.dispatch(simple_workflow)("Hello", "World")
result = ct.get_result(dispatch_id)

lattice = Lattice(
    id=1,
    dispatch_id=dispatch_id,
    name=simple_workflow.__name__,
    status=str(result._status),
    storage_type="local",
    storage_path=dispatch_id,
    function_filename="dispatch_source.pkl",
    function_string_filename="dispatch_source.py",
    executor_filename="executor.pkl",
    error_filename="error.txt",
    inputs_filename="inputs.pkl",
    results_filename="result.pkl",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    started_at=result._start_time,
    completed_at=result._end_time,
)

electron = Electron(
    id=1,
    parent_lattice_id=lattice.id,
    transport_graph_node_id=result.lattice.transport_graph.get_topologically_sorted_graph()[0][0],
    type=ElectronTypeEnum.electron,
    name=join_words.__name__,
    status=str(result._status),
    storage_type="local",
    storage_path=dispatch_id,
    function_filename="dispatch_source.pkl",
    function_string_filename="dispatch_source.py",
    executor_filename="executor.pkl",
    error_filename="error.txt",
    results_filename="result.pkl",
    value_filename="value.pkl",
    stdout_filename="stdout.log",
    stderr_filename="stderr.log",
    info_filename="result_info.yaml",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    started_at=result._start_time,
    completed_at=result._end_time,
)


with Session(engine) as session:
    session.add(lattice)
    session.add(electron)
    session.commit()

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--show-tables", action="store_true")
args = parser.parse_args()
if args.show_tables:
    import pandas as pd

    for table in tables:
        sql_table = pd.read_sql_table(table_name=table, con=engine)
        print(sql_table)
