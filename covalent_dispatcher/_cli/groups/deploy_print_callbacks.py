# Copyright 2023 Agnostiq Inc.
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


"""Print callbacks for deploy up and deploy down commands."""

import re
from typing import Union

from rich.console import Console
from rich.status import Status


class ScrollBufferCallback:
    """Callable print callback that refreshes a buffer of length `max_lines`"""

    _complete_msg_pattern = re.compile(
        r"^(Apply complete\! Resources: \d+ added, \d+ changed, \d+ destroyed\."
        "|"
        r"Destroy complete\! Resources: \d+ destroyed\.)$"
    )

    def __init__(
        self,
        console: Console,
        console_status: Status,
        msg_template: str,
        verbose: bool,
        max_lines: int = 12,
    ):
        """Create a new scroll buffer callback.

        Args:
            console: Rich console object.
            console_status: Rich console status object.
            msg_template: Message template pre-formatted with provision or destroy message.
            verbose: Whether to print the output inline or not.
            max_lines: Number of lines in the buffer. Defaults to 5.
        """
        self.console = console
        self.console_status = console_status
        self.msg_template = msg_template
        self.verbose = verbose
        self.max_lines = max_lines
        self.buffer = []

        self._complete_msg = None

    @property
    def complete_msg(self) -> Union[str, None]:
        """Return a complete message matching:

            'Apply complete! Resources: 19 added, 0 changed, 0 destroyed.'
        or
            'Destroy complete! Resources: 19 destroyed.'

        Returns:
            The complete message, if it exists, else None.
        """
        return self._complete_msg

    def __call__(self, msg: str):
        if self.verbose:
            self._verbose_print(msg)
        else:
            self._inline_print(msg)

    def _inline_print(self, msg: str) -> None:
        """Print into a scrolling buffer of size `self.max_lines`."""
        if len(self.buffer) > self.max_lines:
            self.buffer.pop(0)
        self.buffer.append(msg)

        if self._complete_msg_pattern.match(msg):
            self._complete_msg = msg

        text = self.render_buffer()
        self.console_status.update(self.msg_template.format(text=text))

    def _verbose_print(self, msg: str) -> None:
        """Print normally, line by line."""
        print(msg.rstrip() if msg != "\n" else msg)

    def render_buffer(self, sep: str = " ") -> str:
        """Render the current buffer as a string."""
        return sep.join(self.buffer)
