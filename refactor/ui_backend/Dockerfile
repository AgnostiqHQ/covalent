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
ENV PROJECT_DIR=/ui_backend
ENV FE_PORT 8005
ENV BE_PORT 8004
EXPOSE $BE_PORT $FE_PORT

RUN apt-get update \
  && apt-get install -y --no-install-recommends git gcc g++ make curl\
  && curl -sL https://deb.nodesource.com/setup_16.x | bash - \
  && apt-get install -y nodejs \
  && npm install --global yarn \
  && cd /usr/local/bin \
  && pip3 install --upgrade pip \
  && rm -rf /var/lib/apt/lists/*


RUN mkdir -p $PROJECT_DIR && chmod 0777 $PROJECT_DIR

COPY refactor/ui_backend/ $PROJECT_DIR
COPY refactor/ $PROJECT_DIR/refactor
COPY refactor/ui_backend/webapp $PROJECT_DIR/webapp
COPY covalent/ $PROJECT_DIR/covalent
COPY covalent_dispatcher/ $PROJECT_DIR/covalent_dispatcher
COPY covalent_ui/ $PROJECT_DIR/covalent_ui
COPY ["setup.py", "VERSION", "README.md", "$PROJECT_DIR/"]

RUN pip3 install  --no-cache-dir --upgrade -r $PROJECT_DIR/requirements/dist.txt
RUN cd $PROJECT_DIR/webapp \
    && yarn install --network-timeout 100000 \
    && yarn build --network-timeout 100000

WORKDIR $PROJECT_DIR
CMD [ "python", "main.py"]
