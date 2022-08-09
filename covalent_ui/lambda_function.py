
import os
import boto3
import cloudpickle as pickle

def lambda_handler(event, context):
    os.environ['HOME'] = "/tmp"
    os.chdir("/tmp")

    s3 = boto3.client("s3")

    try:
        s3.download_file("covalent-lambda-job-resources", "func-004335f9-47da-482d-abd1-9108924e985e-0.pkl", "/tmp/func-004335f9-47da-482d-abd1-9108924e985e-0.pkl")
    except Exception as e:
        print(e)

    with open("/tmp/func-004335f9-47da-482d-abd1-9108924e985e-0.pkl", "rb") as f:
        function, args, kwargs = pickle.load(f)

    try:
        result = function(*args, **kwargs)
    except Exception as e:
        print(e)

    with open("/tmp/result-004335f9-47da-482d-abd1-9108924e985e-0.pkl", "wb") as f:
        pickle.dump(result, f)

    try:
        s3.upload_file("/tmp/result-004335f9-47da-482d-abd1-9108924e985e-0.pkl", "covalent-lambda-job-resources", "result-004335f9-47da-482d-abd1-9108924e985e-0.pkl")
    except Exception as e:
        print(e)
