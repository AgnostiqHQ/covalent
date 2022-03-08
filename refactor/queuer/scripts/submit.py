import requests
import os
import base64

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, './result.pkl')

with open(filename, 'rb') as f:
    
    # encode binary to base64
    result_binary = f.read()
    result_base64 = base64.b64encode(result_binary).decode('utf-8')

    body = {
        "result_object": result_base64
    }
    res = requests.post(url='http://localhost:8000/api/v0/submit/dispatch', json=body)