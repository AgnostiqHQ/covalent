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

"""Results management service."""

import logging
import os
import sqlite3

# setup loggers
logging.config.fileConfig("../../../../logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

results_db = os.environ.get("RESULTS_DB")
if not results_db:
    results_db = "results.db"
con = sqlite3.connect(results_db)
cur = con.cursor()
sql = (
    "CREATE TABLE IF NOT EXISTS results ("
    "dispatch_id text NOT NULL, "
    "filename text NOT NULL, "
    "path text NOT NULL, "
    "PRIMARY KEY (dispatch_id))"
)
logger.info("Executing SQL command.")
logger.info(sql)
cur.execute(sql)
con.commit()
con.close()
