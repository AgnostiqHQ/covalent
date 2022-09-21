/**
 * Copyright 2021 Agnostiq Inc.
 *
 * This file is part of Covalent.
 *
 * Licensed under the GNU Affero General Public License 3.0 (the "License").
 * A copy of the License may be obtained with this software package or at
 *
 *      https://www.gnu.org/licenses/agpl-3.0.en.html
 *
 * Use of this file is prohibited except in compliance with the License. Any
 * modifications or derivative works of this file must retain this copyright
 * notice, and modified files must contain a notice indicating that they have
 * been altered from the originals.
 *
 * Covalent is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
 *
 * Relief from the License may be granted by purchasing a commercial license.
 */
const logsDemoData = {
    logList:
        [
            {
                "log_date": "2022-09-21 09:07:20.497000",
                "status": "WARNING",
                "message": "127.0.0.1:45890 - \"GET /api/v1/dispatches/overview HTTP/1.1\" 200"
            },
            {
                "log_date": "2022-09-21 09:07:20.485000",
                "status": "WARN",
                "message": "127.0.0.1:45888 - \"GET /api/v1/dispatches/list?count=10&offset=0&search=&sort_by=started_at&sort_direction=desc&status_filter=ALL HTTP/1.1\" 200"
            },
            {
                "log_date": "2022-09-21 09:07:20.343000",
                "status": "CRITICAL",
                "message": "127.0.0.1:45888 - \"GET /socket.io/?EIO=4&transport=polling&t=ODVJJgL HTTP/1.1\" 200"
            },
            {
                "log_date": "2022-09-21 09:07:20.178000",
                "status": "ERROR",
                "message": "127.0.0.1:45888 - \"GET /static/js/2.71f4b899.chunk.js HTTP/1.1\" 200"
            },
            {
                "log_date": "2022-09-21 09:03:33.121000",
                "status": "INFO",
                "message": "127.0.0.1:45294 - \"POST /api/webhook HTTP/1.1\" 200\nemitting event \"result-update\" to all [/]"
            }
        ]
    ,
    total_count: 5
}

export default logsDemoData
