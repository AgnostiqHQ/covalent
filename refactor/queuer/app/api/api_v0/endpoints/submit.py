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

import os 

from app.schemas.submit import ResultPickle, SubmitResponse
from fastapi import APIRouter, File
from refactor.queuer.app.core.api import DataService
from refactor.queuer.app.core.queuer import Queuer

router = APIRouter()

@router.post("/dispatch", status_code=202, response_model=SubmitResponse)
async def submit_workflow(*, result_pkl_file: bytes = File(...)) -> SubmitResponse:
    """
    Note: The object that contains the workflow function, interface to
    update attributes in the transport graph, inputs of the workflow,
    metadata, etc. is the result object that's why its type is ResultPickle
    which contains the pickled result object. Its use however varies in
    different components. We call it the result object because it is supposed
    to be the ultimate thing the user will get and will contain everything in the workflow.
    """

    queue = Queuer()
    data_svc = DataService()

    created_result = await data_svc.create_result(result_pkl_file)

    dispatch_id = created_result["dispatch_id"]
    
    await queue.publish(queue.topics.DIPATCH, {
        "dispatch_id": dispatch_id
    })

    return {
        "dispatch_id": dispatch_id
    }