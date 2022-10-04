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
import re
from datetime import datetime

from fastapi.responses import Response

from covalent._shared_files.config import get_config
from covalent_ui.api.v1.models.logs_model import LogsResponse

UI_LOGFILE = get_config("user_interface.log_dir") + "/covalent_ui.log"


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
                else:
                    output_arr[len(output_arr) - 1] += last_msg
                last_msg = ""
                output_arr.append(line)
        else:
            last_msg += line + "\n"
        return last_msg

    def __split_merge_json(self, line, regex_expr, result_data, search):
        reg = regex_expr.split(line.rstrip("\n"))
        json_data = {"log_date": None, "status": "INFO", "message": reg[0]}
        if len(reg) >= 3:
            parse_str = datetime.strptime(reg[1], "%Y-%m-%d %H:%M:%S,%f")
            json_data = {"log_date": f"{parse_str}", "status": reg[2], "message": reg[3]}
        if search != "":
            if (search in json_data["message"].lower()) or (search in json_data["status"].lower()):
                result_data.append(json_data)
        else:
            result_data.append(json_data)

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
        last_msg = ""
        reverse_list = direction.value == "DESC"

        split_line, split_words = (
            r"\[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,3})?,[0-9]+]"
        ), (
            r"\[(.*)\] \[(TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|SEVERE|CRITICAL|FATAL)\] ((.|\n)*)"
        )

        try:
            with open(UI_LOGFILE, "r", encoding="utf-8") as logfile:
                for line in logfile:
                    last_msg = self.__split_merge_line(output_data, split_line, line, last_msg)
                if last_msg != "":
                    if len(output_data) == 0:
                        output_data.append(last_msg)
                    output_data[len(output_data) - 1] += last_msg
                    last_msg = ""
        except FileNotFoundError:
            output_data = []

        if len(output_data) == 0:
            return LogsResponse(items=[], total_count=len(result_data))

        regex_expr = re.compile(split_words)
        for line in output_data:
            self.__split_merge_json(line, regex_expr, result_data, search.lower())
        modified_data = sorted(
            result_data,
            key=lambda e: (e[sort_by.value] is not None, e[sort_by.value]),
            reverse=reverse_list,
        )

        modified_data = (
            modified_data[offset : count + offset] if count != 0 else modified_data[offset:]
        )

        return LogsResponse(items=modified_data, total_count=len(result_data))

    def download_logs(self):
        """Download logs"""
        data = None
        if os.path.exists(UI_LOGFILE):
            with open(UI_LOGFILE, "rb") as file:
                data = file.read().decode("utf-8")
                return Response(data)
        return {"data": data}
