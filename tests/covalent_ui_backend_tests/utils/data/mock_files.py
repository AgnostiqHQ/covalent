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

"""Mock files data"""

import os
import pickle

from covalent._workflow.transport import TransportableObject, _TransportGraph

with open(
    os.path.dirname(os.path.abspath(__file__)) + "/sample_transport_graph", "rb"
) as sample_file:
    sample_data = pickle.load(sample_file)


def mock_files_data():
    """Mock files data"""
    apply_args = {
        "doc": "Built-in mutable sequence.\n\nIf no argument is given, the constructor creates a new empty list.\nThe argument must be an iterable if specified."
    }
    apply_kwargs = {
        "doc": "dict() -> new empty dictionary\ndict(mapping) -> new dictionary initialized from a mapping object's\n    (key, value) pairs\ndict(iterable) -> new dictionary initialized as if via:\n    d = {}\n    for k, v in iterable:\n        d[k] = v\ndict(**kwargs) -> new dictionary initialized with the name=value pairs\n    in the keyword argument list.  For example:  dict(one=1, two=2)"
    }

    test_function = "<function hello at 0x7fcc2cdb4670>"
    test_object_string = "<function apply_bash_commands at 0x7fcc59d0b040>"

    file_name = {
        "value": "value.pkl",
        "info": "info.log",
        "stdout": "stdout.log",
        "stderr": "stderr.log",
        "call_after": "call_after.pkl",
        "call_before": "call_before.pkl",
        "results": "results.pkl",
        "function": "function.pkl",
        "executor": "executor_data.pkl",
        "deps": "deps.pkl",
        "cova_imports": "cova_imports.pkl",
        "error": "error.log",
        "function_docstring": "function_docstring.txt",
        "function_string": "function_string.txt",
        "inputs": "inputs.pkl",
        "lattice_imports": "lattice_imports.pkl",
    }

    _object_id = "gAWVNwAAAAAAAACMG2NvdmFsZW50Ll93b3JrZmxvdy5kZXBzYmFzaJSME2FwcGx5X2Jhc2hfY29tbWFuZHOUk5Qu"  # pragma: allowlist secret

    transport_graph = _TransportGraph()
    transport_graph.lattice_metadata = {
        "executor": "dask",
        "results_dir": "/home/arunmukesh/Desktop/files/results",
        "workflow_executor": "dask",
        "deps": {},
        "call_before": [],
        "call_after": [],
        "executor_data": {},
        "workflow_executor_data": {},
    }
    transport_graph.dirty_nodes = []
    return {
        "lattice_files": {
            "path": "tests/covalent_ui_backend_tests/utils/mock_files/78525234-72ec-42dc-94a0-f4751707f9cd",
            "files": [
                {"file_name": file_name["call_after"], "data": []},
                {"file_name": file_name["call_before"], "data": []},
                {"file_name": file_name["cova_imports"], "data": {"electron", "ct"}},
                {"file_name": file_name["deps"], "data": {}},
                {"file_name": file_name["error"], "data": ""},
                {"file_name": file_name["executor"], "data": {}},
                {"file_name": file_name["function_docstring"], "data": ""},
                {
                    "file_name": file_name["function"],
                    "data": TransportableObject.make_transportable(test_function),
                },
                {
                    "file_name": file_name["function_string"],
                    "data": """@ct.lattice
def workflow(name):
\tresult=join(hello(),moniker(name))
\treturn result+" !!\"""",
                },
                {
                    "file_name": file_name["inputs"],
                    "data": {
                        "args": [],
                        "kwargs": {"name": TransportableObject.make_transportable("shore")},
                    },
                },
                {
                    "file_name": file_name["lattice_imports"],
                    "data": """# import covalent as ct

                    """,
                },
                {"file_name": "named_args.pkl", "data": {}},
                {"file_name": "named_kwargs.pkl", "data": {}},
                {
                    "file_name": file_name["results"],
                    "data": TransportableObject.make_transportable("Hello shore - lattice  !!"),
                },
                {"file_name": file_name["stderr"], "data": ""},
                {"file_name": file_name["stdout"], "data": ""},
                {
                    "file_name": "transport_graph.pkl",
                    "data": sample_data,
                },
                {"file_name": "workflow_executor_data.pkl", "data": {}},
            ],
        },
        "electron_files_node_0": {
            "path": "tests/covalent_ui_backend_tests/utils/mock_files/78525234-72ec-42dc-94a0-f4751707f9cd/node_0",
            "files": [
                {"file_name": file_name["call_after"], "data": []},
                {"file_name": file_name["call_before"], "data": []},
                {
                    "file_name": file_name["deps"],
                    "data": {
                        "bash": {
                            "type": "DepsBash",
                            "short_name": "covalent",
                            "attributes": {
                                "commands": [],
                                "apply_fn": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": test_object_string,
                                        "_json": "",
                                        "attrs": {"doc": None, "name": "apply_bash_commands"},
                                    },
                                },
                                "apply_args": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": "[[]]",
                                        "_json": "[[]]",
                                        "attrs": {
                                            "doc": apply_args["doc"],
                                            "name": "",
                                        },
                                    },
                                },
                                "apply_kwargs": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": "{}",
                                        "_json": "{}",
                                        "attrs": {
                                            "doc": apply_kwargs["doc"],
                                            "name": "",
                                        },
                                    },
                                },
                                "retval_keyword": "",
                            },
                        }
                    },
                },
                {"file_name": file_name["executor"], "data": {}},
                {
                    "file_name": file_name["function_string"],
                    "data": """@ct.electron\ndef hello(): return "Hello "\n"
                    """,
                },
                {
                    "file_name": file_name["function"],
                    "data": TransportableObject.make_transportable(test_function),
                },
                {"file_name": file_name["info"], "data": ""},
                {
                    "file_name": file_name["results"],
                    "data": TransportableObject.make_transportable("Hello shore - Node 0 !!"),
                },
                {"file_name": file_name["stderr"], "data": ""},
                {
                    "file_name": file_name["stdout"],
                    "data": """DEBUG: update_electrons_data called on node 5
DEBUG: update_electrons_data called on node 1""",
                },
                {"file_name": file_name["value"], "data": None},
            ],
        },
        "electron_files_node_1": {
            "path": "tests/covalent_ui_backend_tests/utils/mock_files/78525234-72ec-42dc-94a0-f4751707f9cd/node_1",
            "files": [
                {"file_name": file_name["call_after"], "data": []},
                {"file_name": file_name["call_after"], "data": []},
                {
                    "file_name": file_name["deps"],
                    "data": {
                        "bash": {
                            "type": "DepsBash",
                            "short_name": "covalent",
                            "attributes": {
                                "commands": [],
                                "apply_fn": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": test_object_string,
                                        "_json": "",
                                        "attrs": {"doc": None, "name": "apply_bash_commands"},
                                    },
                                },
                                "apply_args": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": "[[]]",
                                        "_json": "[[]]",
                                        "attrs": {
                                            "doc": apply_args["doc"],
                                            "name": "",
                                        },
                                    },
                                },
                                "apply_kwargs": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": "{}",
                                        "_json": "{}",
                                        "attrs": {
                                            "doc": apply_kwargs["doc"],
                                            "name": "",
                                        },
                                    },
                                },
                                "retval_keyword": "",
                            },
                        }
                    },
                },
                {"file_name": file_name["executor"], "data": {}},
                {
                    "file_name": file_name["function_string"],
                    "data": "None",
                },
                {
                    "file_name": file_name["function"],
                    "data": TransportableObject.make_transportable(test_function),
                },
                {"file_name": file_name["info"], "data": ""},
                {
                    "file_name": file_name["results"],
                    "data": TransportableObject.make_transportable("Hello shore - Node 1  !!"),
                },
                {"file_name": file_name["stderr"], "data": ""},
                {"file_name": file_name["stdout"], "data": ""},
                {"file_name": file_name["value"], "data": None},
            ],
        },
        "electron_files_node_2": {
            "path": "tests/covalent_ui_backend_tests/utils/mock_files/78525234-72ec-42dc-94a0-f4751707f9cd/node_2",
            "files": [
                {"file_name": file_name["call_after"], "data": []},
                {"file_name": file_name["call_after"], "data": []},
                {
                    "file_name": file_name["deps"],
                    "data": {
                        "bash": {
                            "type": "DepsBash",
                            "short_name": "covalent",
                            "attributes": {
                                "commands": [],
                                "apply_fn": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": test_object_string,
                                        "_json": "",
                                        "attrs": {"doc": None, "name": "apply_bash_commands"},
                                    },
                                },
                                "apply_args": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": "[[]]",
                                        "_json": "[[]]",
                                        "attrs": {
                                            "doc": apply_args["doc"],
                                            "name": "",
                                        },
                                    },
                                },
                                "apply_kwargs": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": "{}",
                                        "_json": "{}",
                                        "attrs": {
                                            "doc": apply_kwargs["doc"],
                                            "name": "",
                                        },
                                    },
                                },
                                "retval_keyword": "",
                            },
                        }
                    },
                },
                {"file_name": file_name["executor"], "data": {}},
                {
                    "file_name": file_name["function_string"],
                    "data": """@ct.electron\ndef hello World(): return "Hello "\n""",
                },
                {
                    "file_name": file_name["function"],
                    "data": TransportableObject.make_transportable(test_function),
                },
                {"file_name": file_name["info"], "data": ""},
                {
                    "file_name": file_name["results"],
                    "data": TransportableObject.make_transportable("Hello shore - Node 2 !!"),
                },
                {"file_name": file_name["stderr"], "data": ""},
                {"file_name": file_name["stdout"], "data": ""},
                {"file_name": file_name["value"], "data": None},
            ],
        },
        "electron_files_node_3": {
            "path": "tests/covalent_ui_backend_tests/utils/mock_files/78525234-72ec-42dc-94a0-f4751707f9cd/node_3",
            "files": [
                {"file_name": file_name["call_after"], "data": []},
                {"file_name": file_name["call_after"], "data": []},
                {
                    "file_name": file_name["deps"],
                    "data": {
                        "bash": {
                            "type": "DepsBash",
                            "short_name": "covalent",
                            "attributes": {
                                "commands": [],
                                "apply_fn": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": test_object_string,
                                        "_json": "",
                                        "attrs": {"doc": None, "name": "apply_bash_commands"},
                                    },
                                },
                                "apply_args": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": "[[]]",
                                        "_json": "[[]]",
                                        "attrs": {
                                            "doc": apply_args["doc"],
                                            "name": "",
                                        },
                                    },
                                },
                                "apply_kwargs": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": "{}",
                                        "_json": "{}",
                                        "attrs": {
                                            "doc": apply_kwargs["doc"],
                                            "name": "",
                                        },
                                    },
                                },
                                "retval_keyword": "",
                            },
                        }
                    },
                },
                {"file_name": file_name["executor"], "data": {}},
                {
                    "file_name": file_name["function_string"],
                    "data": """@ct.electron\ndef pipeline(): return "Pipeline tasks started "\n""",
                },
                {
                    "file_name": file_name["function"],
                    "data": TransportableObject.make_transportable(test_function),
                },
                {"file_name": file_name["info"], "data": ""},
                {
                    "file_name": file_name["results"],
                    "data": TransportableObject.make_transportable("Hello shore - Node 3 !!"),
                },
                {"file_name": file_name["stderr"], "data": ""},
                {"file_name": file_name["stdout"], "data": ""},
                {"file_name": file_name["value"], "data": None},
            ],
        },
        "electron_files_node_4": {
            "path": "tests/covalent_ui_backend_tests/utils/mock_files/78525234-72ec-42dc-94a0-f4751707f9cd/node_4",
            "files": [
                {"file_name": file_name["call_after"], "data": []},
                {"file_name": file_name["call_after"], "data": []},
                {
                    "file_name": file_name["deps"],
                    "data": {
                        "bash": {
                            "type": "DepsBash",
                            "short_name": "covalent",
                            "attributes": {
                                "commands": [],
                                "apply_fn": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": test_object_string,
                                        "_json": "",
                                        "attrs": {"doc": None, "name": "apply_bash_commands"},
                                    },
                                },
                                "apply_args": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": "[[]]",
                                        "_json": "[[]]",
                                        "attrs": {
                                            "doc": apply_args["doc"],
                                            "name": "",
                                        },
                                    },
                                },
                                "apply_kwargs": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": "{}",
                                        "_json": "{}",
                                        "attrs": {
                                            "doc": apply_kwargs["doc"],
                                            "name": "",
                                        },
                                    },
                                },
                                "retval_keyword": "",
                            },
                        }
                    },
                },
                {"file_name": file_name["executor"], "data": {}},
                {
                    "file_name": file_name["function_string"],
                    "data": "None",
                },
                {
                    "file_name": file_name["function"],
                    "data": TransportableObject.make_transportable(test_function),
                },
                {"file_name": file_name["info"], "data": ""},
                {
                    "file_name": file_name["results"],
                    "data": TransportableObject.make_transportable("Hello shore - Node 4 !!"),
                },
                {"file_name": file_name["stderr"], "data": ""},
                {"file_name": file_name["stdout"], "data": ""},
                {"file_name": file_name["value"], "data": None},
            ],
        },
        "electron_files_node_5": {
            "path": "tests/covalent_ui_backend_tests/utils/mock_files/78525234-72ec-42dc-94a0-f4751707f9cd/node_5",
            "files": [
                {"file_name": file_name["call_after"], "data": []},
                {"file_name": file_name["call_after"], "data": []},
                {
                    "file_name": file_name["deps"],
                    "data": {
                        "bash": {
                            "type": "DepsBash",
                            "short_name": "covalent",
                            "attributes": {
                                "commands": [],
                                "apply_fn": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": test_object_string,
                                        "_json": "",
                                        "attrs": {"doc": None, "name": "apply_bash_commands"},
                                    },
                                },
                                "apply_args": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": "[[]]",
                                        "_json": "[[]]",
                                        "attrs": {
                                            "doc": apply_args["doc"],
                                            "name": "",
                                        },
                                    },
                                },
                                "apply_kwargs": {
                                    "type": "TransportableObject",
                                    "attributes": {
                                        "_object": _object_id,
                                        "python_version": "3.8.10",
                                        "object_string": "{}",
                                        "_json": "{}",
                                        "attrs": {
                                            "doc": apply_kwargs["doc"],
                                            "name": "",
                                        },
                                    },
                                },
                                "retval_keyword": "",
                            },
                        }
                    },
                },
                {"file_name": file_name["executor"], "data": {}},
                {
                    "file_name": file_name["function_string"],
                    "data": "None",
                },
                {
                    "file_name": file_name["function"],
                    "data": TransportableObject.make_transportable(test_function),
                },
                {"file_name": file_name["info"], "data": ""},
                {
                    "file_name": file_name["results"],
                    "data": TransportableObject.make_transportable("Hello shore - Node 5 !!"),
                },
                {"file_name": file_name["stderr"], "data": ""},
                {"file_name": file_name["stdout"], "data": ""},
                {"file_name": file_name["value"], "data": None},
            ],
        },
        "log_files": {
            "path": "tests/covalent_ui_backend_tests/utils/mock_files/log_files",
            "files": [
                {
                    "file_name": "case_1.log",
                    "data": """[2022-09-23 07:43:59,752] [INFO] Started server process [41482]
[2022-09-23 07:43:59,753] [INFO] Waiting for application startup.
[2022-09-23 07:44:01,753] [INFO] Application startup complete.
[2022-09-26 07:44:16,411] [INFO] 127.0.0.1:47378 - "GET /docs HTTP/1.1" 200
[2022-09-26 07:45:27,907] [INFO] 127.0.0.1:47378 - "GET /openapi.json HTTP/1.1" 200""",
                },
                {
                    "file_name": "case_2.log",
                    "data": """[2022-09-23 11:08:56,752] [INFO] Started server process [41482]
[2022-09-23 12:30:51,753] [INFO] Waiting for application startup.
[2022-09-23 12:31:59,753] [INFO] Application startup complete.
[2022-09-26 12:36:42,411] [INFO] 127.0.0.1:47378 - "GET /docs HTTP/1.1" 200
[2022-09-26 13:41:31,907] [INFO] 127.0.0.1:47378 - "GET /openapi.json HTTP/1.1" 200
connection Closed
Killed
[2022-09-26 13:53:12,907] [INFO] WebSocket - connection open
[2022-09-26 13:53:59,907] [INFO] 127.0.0.1:47378 - "GET /favicon.ico HTTP/1.1" 404""",
                },
                {
                    "file_name": "case_3.log",
                    "data": """Killed
[2022-09-23 03:01:52,752] [INFO] Started server process [41482]
[2022-09-23 03:11:11,753] [INFO] Waiting for application startup.
[2022-09-23 03:43:57,753] [INFO] Application startup complete.
[2022-09-26 05:14:33,411] [INFO] 127.0.0.1:47378 - "GET /docs HTTP/1.1" 200
[2022-09-26 05:28:54,907] [INFO] 127.0.0.1:47378 - "GET /openapi.json HTTP/1.1" 200
connection Closed
[2022-09-26 06:00:42,907] [INFO] WebSocket - connection open
[2022-09-26 06:36:46,907] [INFO] 127.0.0.1:47378 - "GET /favicon.ico HTTP/1.1" 404
Connection Closed
killed""",
                },
                {
                    "file_name": "case_4.log",
                    "data": "",
                },
            ],
        },
    }
