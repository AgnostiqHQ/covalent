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
ENV PROJECT_DIR=/runner
ENV COVALENT_ROOT=/covalent
ENV PORT 8002
EXPOSE $PORT

RUN apt-get update \
  && apt-get install -y --no-install-recommends git gcc g++ make \
  && cd /usr/local/bin \
  && pip3 install --upgrade pip \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir $PROJECT_DIR
RUN chmod 0777 $PROJECT_DIR

COPY covalent/ $COVALENT_ROOT/covalent
COPY covalent_dispatcher/ $COVALENT_ROOT/covalent_dispatcher
COPY covalent_ui/ $COVALENT_ROOT/covalent_ui
COPY ["setup.py", "requirements.txt", "VERSION", "README.md", "$COVALENT_ROOT/"]
RUN pip3 install $COVALENT_ROOT

COPY refactor/runner $PROJECT_DIR
WORKDIR $PROJECT_DIR
CMD [ "python", "main.py"]

