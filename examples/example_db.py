#!/usr/bin/env python3

import covalent as ct
from covalent._data_store import DataStore, Electron, ElectronDependency, Lattice


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
session = db.begin_session()
engine = db._get_engine()
print(engine.table_names())
dispatch_id = ct.dispatch(simple_workflow)("Hello", "World")
result = ct.get_result(dispatch_id)

# lattice = Lattice(dispatch_id=dispatch_id,name=simple_workflow.__name__,status=result.status(),storage_type='local',storage_path=dispatch_id,
