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
import os
import re
from datetime import datetime

from fastapi.responses import Response

from covalent._shared_files.config import get_config

UI_LOGFILE = get_config("user_interface.log_dir") + "/covalent_ui.log"


class Logs:
    """Logs data access layer"""

    def __init__(self) -> None:
        self.config = get_config

    def get_logs(self, sort_by, direction, search, count, offset):
        with open(UI_LOGFILE, "r", encoding="utf-8") as logfile:
            search.lower()
            unmatch_str = ""
            log = []
            reverse_list = direction.value == "DESC"
            for i in logfile:
                split_reg = r"\[(.*)\] \[(TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|SEVERE|CRITICAL|FATAL)\]"  # r"\[(.*)\] \[(.*)\] ((.|\n)*)"
                data = re.split(pattern=split_reg, string=i)
                if len(data) > 1:
                    try:
                        parse_str = datetime.strptime(data[1], "%Y-%m-%d %H:%M:%S,%f")
                        json_data = {
                            "log_date": f"{parse_str}",
                            "status": data[2],
                            "message": data[3],
                        }
                    except ValueError:
                        json_data = {"log_date": f"{None}", "status": data[2], "message": data[1:]}
                    log.append(json_data)
                else:
                    len_log = len(log)
                    unmatch_str += i
                    if len_log > 0 and ((unmatch_str != "")):
                        msg = log[len_log - 1]["message"] + "\n"
                        log[len_log - 1]["message"] = msg + unmatch_str
                        unmatch_str = ""
                    else:
                        log.append({"log_date": None, "status": "INFO", "message": unmatch_str})
                        unmatch_str = ""
            log = [
                i
                for i in log
                if (i["message"].lower().__contains__(search))
                or (i["status"].lower().__contains__(search))
            ]
            result = sorted(
                log,
                key=lambda e: (e[sort_by.value] is not None, e[sort_by.value]),
                reverse=reverse_list,
            )
            total_count = len(result)
            result = result[offset : count + offset] if count != 0 else log[offset:]
            return {"items": result, "total_count": total_count}

    def download_logs(self):
        """Download logs"""
        data = None
        if os.path.exists(UI_LOGFILE):
            with open(UI_LOGFILE, "rb") as file:
                data = file.read().decode("utf-8")
                return Response(data)
        return {"data": data}
