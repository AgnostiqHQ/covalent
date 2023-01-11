# syntax=docker/dockerfile:1.4
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

#######################
# Docker Build Options
#######################

# Options are local,pypi,sha
ARG COVALENT_SOURCE=local
# Options are sdk,server
ARG COVALENT_INSTALL_TYPE=server
# Must include a compatible version of Python
ARG BASE_IMAGE=docker.io/python:3.8-slim-bullseye

###################
# Covalent Options
###################

# Installation path
ARG COVALENT_ROOT=/var/lib/covalent
# Configuration file path
ARG COVALENT_CONFIG_DIR=/etc/covalent
# Service port for dispatcher / UI
ARG COVALENT_SVC_PORT=48008
# Local plugins path
ARG COVALENT_PLUGINS_DIR=/etc/covalent/plugins
# SQLite database path (do not use in production)
ARG COVALENT_DATABASE=/var/lib/covalent/dispatch.db
# Remote database path (overrides SQLite database if defined)
ARG COVALENT_DATABASE_URL=""
# Local object storage path
ARG COVALENT_DATA_DIR=/var/lib/covalent/data
# Log file path
ARG COVALENT_LOGDIR=/var/log/covalent
# Cache path
ARG COVALENT_CACHE_DIR=/var/cache/covalent
# Debug mode
ARG COVALENT_DEBUG_MODE=1

########################
# Covalent Dask Options
########################

# Disable Dask inside the container
ARG COVALENT_DISABLE_DASK=1
# Number of Dask workers used by dispatcher
ARG COVALENT_NUM_WORKERS=1
# Number of threads per Dask worker
ARG COVALENT_THREADS_PER_WORKER=1
# Memory per worker (in GB)
ARG COVALENT_MEM_PER_WORKER=1GB

# Global settings
FROM ${BASE_IMAGE} as base

ENV PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    BUILDROOT=/build \
    INSTALLROOT=${COVALENT_ROOT} \
    USER=covalent \
    COVALENT_ROOT=${COVALENT_ROOT} \
    COVALENT_CONFIG_DIR=${COVALENT_CONFIG_DIR} \
    COVALENT_PLUGINS_DIR=${COVALENT_PLUGINS_DIR} \
    COVALENT_LOGDIR=${COVALENT_LOGDIR} \
    COVALENT_CACHE_DIR=${COVALENT_CACHE_DIR}

USER root

RUN <<EOL
  mkdir -p \
    ${COVALENT_CONFIG_DIR} \
    ${COVALENT_PLUGINS_DIR} \
    ${COVALENT_DATA_DIR} \
    ${COVALENT_LOGDIR} \
    ${COVALENT_CACHE_DIR}
  chown -R ${USER}:${USER} \
    ${COVALENT_CONFIG_DIR} \
    ${COVALENT_PLUGINS_DIR} \
    ${COVALENT_DATA_DIR} \
    ${COVALENT_LOGDIR} \
    ${COVALENT_CACHE_DIR}
EOL

WORKDIR ${BUILDROOT}

# Tools required for all build patterns
FROM base AS build_base

RUN <<EOL
  apt-get update
  apt-get install -y --no-install-recommends \
    git \
    rsync \
    unzip \
    vim \
    wget
  rm -rf /var/lib/apt/lists/*
  python -m venv --copies $BUILDROOT/.venv
  python -m pip install --upgrade pip
EOL

ENV PATH=$BUILDROOT/.venv/bin:$PATH

ENTRYPOINT [ "/bin/bash" ]

# Settings required to create an SDK-only container
FROM build_base as build_sdk

ENV COVALENT_SDK_ONLY True

# Tools required to build Covalent from source
FROM build_base as build_server

RUN <<EOL
  apt-get update
  apt-get install -y --no-install-recommends \
    curl \
    gcc
  curl -sL https://deb.nodesource.com/setup_16.x | bash -
  apt-get install -y nodejs
  npm install --global yarn
  rm -rf /var/lib/apt/lists/*
EOL

# Copy Covalent from local source
FROM build_base as covalent_local_src

COPY . $BUILDROOT

# Fetch Covalent from PyPI
FROM build_base as covalent_pypi_src

ARG COVALENT_RELEASE

RUN python -m pip download --no-deps -d $BUILDROOT/dist covalent==${COVALENT_RELEASE}

# Fetch Covalent from GitHub SHA
FROM build_base as covalent_sha_src

ARG COVALENT_COMMIT_SHA

RUN <<EOL
  wget https://github.com/AgnostiqHQ/covalent/archive/${COVALENT_COMMIT_SHA}.zip
  unzip -d $BUILDROOT ${COVALENT_COMMIT_SHA}.zip
  mv $BUILDROOT/covalent-${COVALENT_COMMIT_SHA}/* $BUILDROOT/
EOL

# Alias the Covalent source into a new layer
FROM covalent_${COVALENT_SOURCE}_src as covalent_src

# Build Covalent SDK
FROM build_sdk as covalent_sdk

COPY --from=covalent_src $BUILDROOT/ $BUILDROOT

RUN <<EOL
  if [ ! -d $BUILDROOT/dist ] ; then
    python setup.py sdist
  fi
  python -m pip install dist/covalent-*.tar.gz
EOL

# Build Covalent Server
FROM build_server as covalent_server

LABEL org.opencontainers.image.title="Covalent Build Environment"
LABEL org.opencontainers.image.vendor="Agnostiq"
LABEL org.opencontainers.image.url="https://covalent.xyz"
LABEL org.opencontainers.image.documentation="https://covalent.readthedocs.io"
LABEL org.opencontainers.image.licenses="GNU AGPL v3"
LABEL org.opencontainers.image.base.name="${BASE_IMAGE}"

COPY --from=covalent_src $BUILDROOT/ $BUILDROOT

RUN <<EOL
  if [ ! -d $BUILDROOT/dist ] ; then
    cd $BUILDROOT/covalent_ui/webapp
    yarn install --network-timeout 100000
    yarn build --network-timeout 100000
    cd $BUILDROOT
    python setup.py sdist
  fi
  python -m pip install dist/covalent-*.tar.gz
EOL

# Alias installed Covalent
FROM covalent_${COVALENT_INSTALL_TYPE} as covalent_install

# Production SDK container
FROM base AS prod_sdk

ARG BUILD_DATE
ARG BUILD_VERSION

LABEL org.opencontainers.image.title="Covalent ${COVALENT_INSTALL_TYPE}"
LABEL org.opencontainers.image.vendor="Agnostiq"
LABEL org.opencontainers.image.url="https://covalent.xyz"
LABEL org.opencontainers.image.documentation="https://covalent.readthedocs.io"
LABEL org.opencontainers.image.source="https://github.com/AgnostiqHQ/covalent"
LABEL org.opencontainers.image.licenses="GNU AGPL v3"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.version="${BUILD_VERSION}"
LABEL org.opencontainers.image.revision="${COVALENT_COMMIT_SHA}"
LABEL org.opencontainers.image.base.name="${BASE_IMAGE}"

COPY --from=build_base /usr/bin/rsync /usr/bin/rsync
COPY --from=build_base /usr/lib/x86_64-linux-gnu/libpopt.so.0 /usr/lib/x86_64-linux-gnu/libpopt.so.0

COPY --from=covalent_install $BUILDROOT/.venv/ $INSTALLROOT/.venv

RUN <<EOL
  /usr/sbin/adduser --shell /bin/bash --disabled-password --gecos "" $USER
  chown -R $USER:$USER $INSTALLROOT
EOL

WORKDIR $INSTALLROOT
USER $USER
ENV PATH=$INSTALLROOT/.venv/bin:$PATH

ENTRYPOINT [ "python" ]

# Production server container
FROM prod_sdk as prod_server

COPY --from=build_base /usr/bin/wget /usr/bin/wget
COPY --from=build_base /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0
COPY --from=build_base /usr/lib/x86_64-linux-gnu/libpsl.so.5 /usr/lib/x86_64-linux-gnu/libpsl.so.5

ENV COVALENT_SVC_PORT=${COVALENT_SVC_PORT} \
    COVALENT_DATABASE_DIR=${COVALENT_DATABASE_DIR} \
    COVALENT_DATABASE_URL=${COVALENT_DATABASE_URL} \
    COVALENT_DATA_DIR=${COVALENT_DATA_DIR} \
    COVALENT_DEBUG_MODE=${COVALENT_DEBUG_MODE} \
    COVALENT_NUM_WORKERS=${COVALENT_NUM_WORKERS} \
    COVALENT_THREADS_PER_WORKER=${COVALENT_THREADS_PER_WORKER} \
    COVALENT_MEM_PER_WORKER=${COVALENT_MEM_PER_WORKER} \
    COVALENT_DISABLE_DASK=${COVALENT_DISABLE_DASK} \
    COVALENT_SERVER_IFACE_ANY=1

EXPOSE ${COVALENT_SVC_PORT}

HEALTHCHECK CMD wget --no-verbose --tries=1 --spider http://localhost:${COVALENT_SVC_PORT} || exit 1

RUN sed -i "s#$BUILDROOT#$INSTALLROOT#" $INSTALLROOT/.venv/bin/covalent

ENTRYPOINT [ "/bin/bash" ]

CMD [ "-c", "covalent start --workers ${COVALENT_NUM_WORKERS} --threads-per-worker ${COVALENT_THREADS_PER_WORKER} --mem-per-worker ${COVALENT_MEM_PER_WORKER} --port ${COVALENT_SVC_PORT} && tail -f ${COVALENT_LOGDIR}/covalent_ui.log" ]

FROM prod_${COVALENT_INSTALL_TYPE} as prod
