FROM python:3.8-slim-buster as venv

RUN apt-get update && \
  apt-get install -y --no-install-recommends build-essential && \
  pip install --upgrade pip && \
  rm -rf /var/lib/apt/lists/*

COPY . /app/
RUN cd /app && \
    python -m venv --copies /app/.venv && \
    . /app/.venv/bin/activate && \
    pip install -e .

# Final image
FROM python:3.8-slim-buster as prod

# Placeholders/default environment variables
ENV DATA_SVC_HOST="0.0.0.0"
ENV DATA_SVC_PORT="8004"
ENV FS_STORAGE_BACKEND="local"
ENV FS_LOCAL_STORAGE_ROOT="data"
ENV FS_STORAGE_BUCKET="default"
ENV MINIO_ENDPOINT="localhost:9000"
ENV MINIO_ACCESS_KEY="minioadmin"
ENV MINIO_SECRET_KEY="minioadmin"
ENV MINIO_DISABLE_TLS=""

COPY --from=venv /app/.venv/ /app/.venv
COPY --from=venv /app/covalent/ /app/covalent
COPY --from=venv /app/covalent_ui/ /app/covalent_ui
COPY --from=venv /app/covalent_dispatcher/ /app/covalent_dispatcher
COPY --from=venv /app/refactor/data/ /app/refactor/data

CMD ["/app/.venv/bin/python", "/app/refactor/data/main.py"]