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

FROM python:3.8-slim-buster

RUN apt-get update \
  && apt-get install -y curl gcc \
  && curl -sL https://deb.nodesource.com/setup_16.x | bash - \
  && apt-get install -y nodejs \
  && npm install --global yarn \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/covalent
COPY . /opt/covalent
RUN pip install --no-cache-dir --use-feature=in-tree-build /opt/covalent
RUN cd /opt/covalent/covalent_ui/webapp \
  && yarn install  \
  && yarn build

WORKDIR /opt/covalent

EXPOSE 8080
ENTRYPOINT [ "python" ]
CMD ["/opt/covalent/covalent_ui/app.py", "--port", "8080"]
