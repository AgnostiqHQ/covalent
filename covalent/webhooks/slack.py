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

"""Slack direct message and incoming webhook support."""

import os
from typing import Dict, Optional

import slack_sdk

from .._shared_files.config import get_config, update_config
from .._shared_files.logger import app_log
from .notify import NotifyEndpoint
from .webhook import NotifyWebhook

_SLACK_DEFAULT_CONFIG = {
    "webhooks": {
        "slack": {
            "webhook_url": "",
            "token": os.environ.get("SLACK_API_TOKEN") or "",
            "channel": "",
            "display_name": "",
        },
    },
}

update_config(_SLACK_DEFAULT_CONFIG, override_existing=False)


class NotifySlack(NotifyEndpoint):
    """Slack notification endpoint. Both incoming webhooks and direct messages are supported
    depending on what is provided to the constructor.

    Args:
        webhook_url: A URL to an incoming webhook.
        token: A Slack bot token with permissions users:read, chat:write, groups:write, im:write,
               mpim:write. Begins with xoxb-. Only required if a channel or display_name are
               provided.
        channel: A slack channel ID to direct message.
        display_name: A user's display name to direct message.
    """

    def __init__(
        self,
        webhook_url: str = get_config("webhooks.slack.webhook_url"),
        token: str = get_config("webhooks.slack.token"),
        channel: str = get_config("webhooks.slack.channel"),
        display_name: str = get_config("webhooks.slack.display_name"),
    ):
        self.webhook_url = webhook_url
        self.token = token
        self.channel = channel
        self.display_name = display_name

        if (
            int(bool(self.webhook_url)) + int(bool(self.channel)) + int(bool(self.display_name))
            != 1
        ):
            error_msg = (
                "NotifySlack requires just one of either webhook_url, channel, or display_name."
            )
            app_log.warning(error_msg)
            raise ValueError(error_msg)

        if self.webhook_url:
            self.endpoint = NotifyWebhook(self.webhook_url)
        else:
            self.client = slack_sdk.WebClient(token=self.token)
            # Raises SlackApiError if token is invalid
            self.client.api_test()

        # Convert display name to user ID
        if self.display_name:
            response = self.client.users_list()
            members = response["members"]

            user_id = ""
            for member in members:
                if member["profile"]["display_name"] == self.display_name:
                    user_id = member["id"]
                    break

            if not user_id:
                error_msg = "User does not exist in this workspace."
                app_log.warning(error_msg)
                raise ValueError(error_msg)

            response = self.client.conversations_open(users=[user_id])
            self.channel = response["channel"]["id"]

    def notify(self, message: str) -> None:
        """Notify a Slack endpoint with a message.

        Args:
            message: A message forwarded to an incoming webhook or a bot.
        """
        if not message:
            return

        if self.webhook_url:
            self.endpoint.notify(message)
        else:
            self.client.chat_postMessage(channel=self.channel, text=message)
