import requests
import json

url = "http://127.0.0.1:5000/api/ask"
question = "where are you born?"

payload = json.dumps({"question": question})
headers = {"Content-Type": "application/json"}

response = requests.post(url, data=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    # Handle the response data
    print(data)
else:
    print("Error:", response.text)
