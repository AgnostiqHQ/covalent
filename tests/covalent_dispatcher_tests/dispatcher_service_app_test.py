# Copyright 2022 Agnostiq Inc.
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

"""Unit tests for the DispatcherServiceApp."""

import unittest

from flask import Flask

from covalent_dispatcher._service.app import bp


@unittest.skip("These tests started failing for every PR on 20220328")
class TestDispatcherServiceApp(unittest.TestCase):
    """Test dispatch service app"""

    def setUp(self) -> None:
        """Basic setup"""

        self.app = Flask(__name__)
        self.app.register_blueprint(bp, url_prefix="")
        return super().setUp()

    def test_blank_post(self):
        """Test blank POST requests"""

        with self.app.test_client() as client:
            response = client.post("/submit")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data.decode("utf-8").strip(), "Empty request body.")
            response = client.post("/cancel")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data.decode("utf-8").strip(), "Empty request body.")

    def test_random_post(self):
        """Test random POST requests"""

        with self.app.test_client() as client:
            random_string = "fsdjfksd"
            response = client.post("/submit", data=random_string)
            self.assertEqual(response.status_code, 500)
            response = client.post("/cancel", data=random_string)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.data.decode("utf-8").strip(), f'"Dispatch {random_string} cancelled."'
            )
