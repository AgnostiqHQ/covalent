# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

    host = "http://localhost:48008"
    wait_time = between(0.5, 5)

    @staticmethod
    def serialize_workflow(workflow, lattice_args):
        lattice = ct.lattice(workflow)
        lattice.build_graph(*lattice_args, {})
        json_lattice = lattice.serialize_to_json()
        return json_lattice

    @task
    def submit_identity_workflow(self):
        self.client.post(
            "/api/v2/dispatches/submit", data=self.serialize_workflow(identity_workflow, [1])
        )

    @task
    def submit_horizontal_workflow(self):
        self.client.post(
            "/api/v2/dispatches/submit",
            data=self.serialize_workflow(horizontal_workflow, [random.randint(5, 10)]),
        )

    @task
    def submit_add_multiply_workflow(self):
        self.client.post(
            "/api/v2/dispatches/submit",
            data=self.serialize_workflow(add_multiply_workflow, [1, 2]),
        )
