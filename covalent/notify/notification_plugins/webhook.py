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

"""Generic webhook support."""

import requests

from covalent.notify.notify import NotifyEndpoint

notification_plugin_name = "NotifyWebhook"


class NotifyWebhook(NotifyEndpoint):
    """Webhook notification endpoint. Provide a webhook URL to this class and
    users can send messages to it using the notify method.

    Attributes:
        webhook_url: Notification endpoint address.
    """

    def __init__(
        self,
        webhook_url: str,
    ) -> None:
        self.webhook_url = webhook_url

    def notify(self, message: str) -> None:
        """Notify a webhook endpoint with a message.

        Args:
            message: A message forwarded to a webhook.
        """

        if not message:
            return

        headers = {"content-type": "application/json"}
        payload = {"text": message}

        r = requests.post(self.webhook_url, headers=headers, data=payload)
        r.raise_for_status()
