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

import random

import cloudpickle as pickle
from load_tests.workflows import add_multiply_workflow, horizontal_workflow, identity_workflow
from locust import HttpUser, between, task

import covalent as ct
from tests.load_tests import workflows

pickle.register_pickle_by_value(workflows)


class BasicUser(HttpUser):
    """
    Locust HttpUser instance use to dispatch simple one/two node workflows
    to the Covalent server continuously with a duration anywhere between [0.5, 5] seconds
    """

    host = "http://covalent.balavk.net"
    wait_time = between(0.5, 5)

    @staticmethod
    def serialize_workflow(workflow, lattice_args):
        lattice = ct.lattice(workflow)
        lattice.build_graph(*lattice_args, {})
        json_lattice = lattice.serialize_to_json()
        return json_lattice

    @task
    def submit_identity_workflow(self):
        self.client.post("/api/submit", data=self.serialize_workflow(identity_workflow, [1]))

    @task
    def submit_horizontal_workflow(self):
        self.client.post(
            "/api/submit",
            data=self.serialize_workflow(horizontal_workflow, [random.randint(5, 10)]),
        )

    @task
    def submit_add_multiply_workflow(self):
        self.client.post(
            "/api/submit",
            data=self.serialize_workflow(add_multiply_workflow, [1, 2]),
        )
