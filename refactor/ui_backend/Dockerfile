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

# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

ENV PROJECT_DIR=/covalent_ui
ENV REQ_DIR=/requirements

RUN mkdir $PROJECT_DIR $REQ_DIR
RUN chmod 0777 $PROJECT_DIR $REQ_DIR

WORKDIR $PROJECT_DIR

COPY requirements $REQ_DIR
RUN pip install  --no-cache-dir --upgrade -r $REQ_DIR/dist.txt

COPY . .

ENV PORT 8004
EXPOSE $PORT

CMD [ "python", "main.py"]
