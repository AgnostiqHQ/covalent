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

import pytest

import covalent as ct


@pytest.mark.skip(reason="test not working")
def test_notify_webhook(mocker):
    @ct.electron
    def task(x):
        return x

    mock_notify = mocker.patch(
        "covalent.notify.notification_plugins.webhook.NotifyWebhook.notify", return_value=None
    )
    endpoint = ct.notify.notification_plugins.webhook.NotifyWebhook(webhook_url="test_url")

    @ct.lattice(notify=[endpoint])
    def workflow(x):
        return task(x)

    ct.dispatch_sync(workflow)(x=1)
    mock_notify.assert_called()
