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
    apt-get install -y --no-install-recommends build-essential curl && \
    curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    npm install --global yarn && \
    pip install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

# Create virtualenv and install dependencies
COPY . /app/
RUN cd /app && \
    python -m venv --copies /app/.venv && \
    . /app/.venv/bin/activate && \
    pip install -e . && \
    cd /app/refactor/ui_backend/webapp && \
    yarn install --network-timeout 100000 && \
    yarn build

FROM python:3.8-slim-buster as prod

ENV UI_SVC_HOST="0.0.0.0"
ENV UI_SVC_PORT="8005"

## Placeholders/defaults
## Results service
ENV DATA_OS_SVC_HOST_URI="http://localhost:8006"
ENV PROJECT_DIR=/ui_backend

COPY --from=venv /app/.venv/ /app/.venv
COPY --from=venv /app/covalent/ /app/covalent
COPY --from=venv /app/covalent_ui/ /app/covalent_ui
# Needs to be changed when directories are restructured
COPY --from=venv /app/refactor/ui_backend/ /app/refactor/ui_backend

ENTRYPOINT [ "/app/.venv/bin/python", "/app/refactor/ui_backend/main.py"]
