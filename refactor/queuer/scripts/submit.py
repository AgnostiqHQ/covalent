import requests
import os

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, './result.pkl')

with open(filename, 'rb') as f:   
    res = requests.post(url='http://localhost:8000/api/v0/submit/dispatch', files={'result_pkl_file': f})
    print(res.text)