import requests
from datetime import datetime, timezone, timedelta, time
from requests.auth import HTTPBasicAuth

port = 8000
auth = HTTPBasicAuth("blank", "Password")


obj = {}

#print(obj)

response = requests.post(f"http://127.0.0.1:{port}/revenue/update-incomes/", obj, auth=auth)
if response.status_code == 200:
    print("Successfully updated!")
