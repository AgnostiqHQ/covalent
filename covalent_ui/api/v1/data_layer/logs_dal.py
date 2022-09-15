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

import re
from datetime import datetime

from covalent._shared_files.config import get_config
from covalent_ui.api.v1.models.logs_model import LogsResponse


class Logs:
    """Logs data access layer"""

    def __init__(self) -> None:
        self.config = get_config

    def __split_merge_line(self, output_arr: list, split_reg, line, last_msg=""):
        match = re.match(split_reg, line)
        if match:
            if last_msg == "":
                output_arr.append(line)
            else:
                if len(output_arr) == 0:
                    output_arr.append(last_msg)
                output_arr.append(line)
                output_arr[len(output_arr) - 1] += last_msg
                last_msg = ""
        else:
            last_msg += "\n" + line
        return last_msg

    def get_logs(self, sort_by, direction, search, count, offset):
        """
        Get Logs
        Args:
            req.count: number of rows to be selected
            req.offset: number rows to be skipped
            req.sort_by: sort by field name(run_time, status, started, lattice)
            req.search: search by text
            req.direction: sort by direction ASE, DESC
        Return:
            List of top most Lattices and count
        """
        output_data, result_data = [], []
        file_name, file_location = "covalent_ui.log", self.config("user_interface.log_dir")
        last_msg = ""
        reverse_list = bool(direction.value == "DESC")

        split_line, split_words = (
            r"\[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,3})?,[0-9]+]"
        ), (r"\[(.*)\] \[(TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|SEVERE|FATAL)\] ((.|\n)*)")

        try:
            with open(f"{file_location}/{file_name}", "r") as logfile:
                for line in logfile:
                    msg = self.__split_merge_line(output_data, split_line, line, last_msg)
                    last_msg = msg
                if last_msg != "":
                    if len(output_data) == 0:
                        output_data.append(last_msg)
                    output_data[len(output_data) - 1] += last_msg
                    last_msg = ""
        except FileNotFoundError:
            output_data = []

        if len(output_data) >= 1:
            regex_word = re.compile(split_words)
            for line in output_data:
                reg = regex_word.split(line.rstrip("\n"))
                if len(reg) >= 3:
                    parse_str = datetime.strptime(reg[1], "%Y-%m-%d %I:%M:%S,%f")
                    json_data = {"log_date": f"{parse_str}", "status": reg[2], "message": reg[3]}
                    result_data.append(json_data)
                else:
                    result_data.append({"log_date": None, "status": "INFO", "message": reg[0]})

            modified_data = sorted(
                result_data,
                key=lambda e: (e[sort_by.value] is None, e[sort_by.value]),
                reverse=reverse_list,
            )

            if search != "":
                modified_data = [
                    x
                    for x in modified_data
                    if (search.lower() in x["message"].lower())
                    or (search.lower() in x["status"].lower())
                ]

            modified_data = modified_data[offset:]
            modified_data = modified_data[:count]
        else:
            modified_data = []

        return LogsResponse(items=modified_data, total_count=len(result_data))
