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

"""Tests for webhook notification endpoint class."""

import requests

from covalent.notify.notification_plugins.webhook import NotifyWebhook


def test_notify_webhook_init(mocker):
    endpoint = NotifyWebhook(webhook_url="test_url")
    assert endpoint.webhook_url == "test_url"


def test_notify_webhook_notify(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_request = mocker.patch("requests.post", return_value=mock_response)

    mock_init = mocker.patch(
        "covalent.notify.notification_plugins.webhook.NotifyWebhook.__init__", return_value=None
    )

    endpoint = NotifyWebhook("test_url")
    mock_init.assert_called_once_with("test_url")

    endpoint.webhook_url = "test_url"
    endpoint.notify("test message")

    mock_request.assert_called_once_with(
        "test_url", headers={"content-type": "application/json"}, data={"text": "test message"}
    )
