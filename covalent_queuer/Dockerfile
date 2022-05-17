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
FROM python:3.8-slim-buster as venv

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential unzip && \
    pip install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

# Create virtualenv and install dependencies
COPY . /app/
RUN cd /app && \
    python -m venv --copies /app/.venv && \
    . /app/.venv/bin/activate && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir -r /app/covalent_queuer/requirements/dist.txt

ENV COVA_SDK "true"
RUN cd /app && \
    . /app/.venv/bin/activate && \
    export COVA_SDK="TRUE" && \
    python setup.py install

FROM python:3.8-slim-buster as prod

ENV QUEUER_SVC_HOST="0.0.0.0"
ENV QUEUER_SVC_PORT="8001"

# Placeholders/defaults
# NATS service
ENV MQ_CONNECTION_URI="nats://localhost:4222"
# Dispatch topic
ENV MQ_DISPATCH_TOPIC="workflow.dispatch"

COPY --from=venv /app/.venv/ /app/.venv
COPY --from=venv /app/covalent_queuer/ /app/covalent_queuer

ENV ENV_DEST_DIR "/app"
WORKDIR /app
ENTRYPOINT [ "/app/.venv/bin/python", "/app/covalent_queuer/main.py"]
