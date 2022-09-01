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
FROM python:3.8-slim-bullseye AS build

RUN apt-get update \
  && apt-get install -y --no-install-recommends rsync wget \
  && rm -rf /var/lib/apt/lists/*

RUN python -m venv --copies /covalent/.venv \
  && . /covalent/.venv/bin/activate \
  && pip install --upgrade pip \
  && pip install covalent==0.177.0

FROM python:3.8-slim-bullseye AS prod
LABEL org.label-schema.name="Covalent Server"
LABEL org.label-schema.vendor="Agnostiq"
LABEL org.label-schema.url="https://covalent.xyz"
LABEL org.label-schema.vcs-url="https://github.com/AgnostiqHQ/covalent"
LABEL org.label-schema.vcs-ref="f2e85397ea4609df274a38b03e6e17dcbae6bc52" # pragma: allowlist secret
LABEL org.label-schema.version="0.177.0"
LABEL org.label-schema.docker.cmd="docker run -it -p 8080:8080 -d covalent:latest"
LABEL org.label-schema.schema-version=1.0

COPY --from=build /usr/bin/rsync /usr/bin/rsync
COPY --from=build /usr/lib/x86_64-linux-gnu/libpopt.so.0 /usr/lib/x86_64-linux-gnu/libpopt.so.0

COPY --from=build /usr/bin/wget /usr/bin/wget
COPY --from=build /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0
COPY --from=build /usr/lib/x86_64-linux-gnu/libpsl.so.5 /usr/lib/x86_64-linux-gnu/libpsl.so.5

COPY --from=build /covalent/.venv/ /covalent/.venv

RUN useradd -ms /bin/bash ubuntu \
  && chown ubuntu:users /covalent

WORKDIR /covalent
USER ubuntu

ENV COVALENT_SERVER_IFACE_ANY=1
ENV PATH=/covalent/.venv/bin:$PATH
EXPOSE 8080
HEALTHCHECK CMD wget --no-verbose --tries=1 --spider http://localhost:8080 || exit 1

RUN covalent config \
  && sed -i 's|^results_dir.*$|results_dir = "/covalent/results"|' /home/ubuntu/.config/covalent/covalent.conf

CMD covalent start --ignore-migrations --port 8080 && bash
