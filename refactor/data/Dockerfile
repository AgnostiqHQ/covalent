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
ENV PROJECT_DIR=/data

RUN mkdir $PROJECT_DIR \
    && chmod 0777 $PROJECT_DIR

WORKDIR $PROJECT_DIR

COPY refactor/data/ $PROJECT_DIR
COPY refactor/ $PROJECT_DIR/refactor
RUN pip3 install  --no-cache-dir --upgrade -r $PROJECT_DIR/requirements/dist.txt
RUN cd $PROJECT_DIR/refactor/  \
    && rm -rf client_side/  && rm -rf dispatcher/ \
    && rm -rf executor/ && rm -rf queuer/ \
    && rm -rf results/ && rm -rf runner/  \
    && rm -rf ui_backend/

ENTRYPOINT [ "python", "main.py"]
