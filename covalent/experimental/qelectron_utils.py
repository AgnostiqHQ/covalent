import json
import re
from datetime import datetime
from dataclasses import is_dataclass
from pathlib import Path
from typing import Tuple

from .._shared_files.config import get_config
from .._shared_files import logger
from .covalent_qelectron.quantum_server.database import Database

_QE_DATA_MARKER = "====QELECTRON_DATA===="

app_log = logger.app_log


def print_qelectron_db(dispatch_id: str, node_id: int) -> None:
    """
    Check for QElectron database file and dump it into stdout

    Args(s)
        dispatch_id: Dispatch ID of the workflow
        node_id: ID of the node in the transport graph

    Return(s)
        None
    """
    db_dir = Path(get_config("dispatcher")["qelectron_db_path"]).resolve()
    if not db_dir.exists():
        # qelectron database not found
        return

    # get database as optional JSON string
    db_dict = Database(db_dir).get_db(dispatch_id=dispatch_id, node_id=node_id)
    if not db_dict:
        # qelectron database is empty
        return

    # non-empty database exists, print as marked JSON string
    db_string = json.dumps(db_dict, cls=CustomDBEncoder)
    print("".join([_QE_DATA_MARKER, db_string, _QE_DATA_MARKER]))


class CustomDBEncoder(json.JSONEncoder):
    """
    Enables converting the database dictionary to a JSON string
    """

    def default(self, o):
        if isinstance(o, datetime):
            # qelectron timing information
            return o.isoformat()

        if hasattr(o, "tolist"):
            # numpy arrays and pennylane tensors
            return o.tolist()

        if is_dataclass(o):
            # qiskit primitive results as dataclasses (e.g. `SamplerResult`)
            return str(o)

        return super().default(o)


def extract_qelectron_db(s: str) -> Tuple[str, dict]:
    """
    Detect Qelectron data in `s` and process into dict if found

    Arg(s):
        s: captured stdout string from a node in the transport graph

    Return(s):
        s_without_db: captured stdout string without Qelectron data
        data_dict: dictionary containing extracted data
    """
    pattern = f"{_QE_DATA_MARKER}(.*){_QE_DATA_MARKER}"

    if not s or not (match := re.match(pattern, s)):
        app_log.debug("No Qelectron data detected")
        return s, {}

    # load json string into dictionary
    app_log.debug("Detected Qelectron output data")
    data_dict = json.loads(match.groups()[0])

    # remove json string from `s`
    s_without_db = re.sub(pattern, "", s).strip()

    return s_without_db, data_dict
