FROM python:3.8-slim-bullseye AS build

RUN apt-get update \
  && mkdir /covalent \
  && python -m venv --copies /covalent/.venv \
  && . /covalent/.venv/bin/activate \
  && pip install --upgrade pip \
  && pip install covalent

FROM python:3.8-slim-bullseye AS prod

RUN apt-get update \
  && apt-get install -y --no-install-recommends rsync \
  && rm -rf /var/lib/apt/lists/*

COPY --from=build /covalent/.venv /covalent/.venv

RUN cat <<EOF > /covalent/exec.py
import os
import boto3
import cloudpickle as pickle

s3_bucket = os.environ["S3_BUCKET_NAME"]
if not s3_bucket:
    raise ValueError("Environment variable S3_BUCKET_NAME was not found")

func_filename = os.environ["FUNC_FILENAME"]
if not func_filename:
    raise ValueError("Environment variable FUNC_FILENAME was not found")

result_filename = os.environ["RESULT_FILENAME"]
if not result_filename:
    raise ValueError("Environment variable RESULT_FILENAME was not found")

local_func_filename = os.path.join("/covalent", func_filename)
local_result_filename = os.path.join("/covalent", result_filename)

s3 = boto3.client("s3")
s3.download_file(s3_bucket, func_filename, local_func_filename)

with open(local_func_filename, "rb") as f:
    function, args, kwargs = pickle.load(f)

result = function(*args, **kwargs)

with open(local_result_filename, "wb") as f:
    pickle.dump(result, f)

s3.upload_file(local_result_filename, s3_bucket, result_filename)
EOF

ENTRYPOINT [ "python" ]
CMD [ "/covalent/exec.py" ]
