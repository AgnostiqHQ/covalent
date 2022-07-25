import subprocess

import covalent as ct
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import _TransportGraph, encode_metadata


def test_lattice_json_serialization():
    @ct.electron(executor="local", deps_bash=ct.DepsBash("yum install gcc"))
    def f(x):
        return x * x

    @ct.lattice
    def workflow(x):
        return f(x)

    workflow.build_graph(5)

    json_workflow = workflow.serialize_to_json()

    new_workflow = Lattice.deserialize_from_json(json_workflow)

    for key in workflow.__dict__:
        if key == "metadata" or key == "transport_graph":
            continue
        assert workflow.__dict__[key] == new_workflow.__dict__[key]

    assert (
        workflow.transport_graph.serialize_to_json()
        == new_workflow.transport_graph.serialize_to_json()
    )

    assert json_workflow == new_workflow.serialize_to_json()
