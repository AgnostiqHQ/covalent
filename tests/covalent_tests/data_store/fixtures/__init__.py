import datetime

import pytest

from covalent._data_store import models


@pytest.fixture
def workflow_fixture():
    """A collection of DB models to be re-used in unit tests for DB"""

    electron_dependency = models.ElectronDependency(
        electron_id=2, parent_electron_id=1, edge_name="arg_1", created_at=datetime.datetime.now()
    )

    return {"electron_dependency": [electron_dependency]}
