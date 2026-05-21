import requests
import json

url = "http://127.0.0.1:8000/chat"
data = {
    "text": "Hello 2",
    "history": json.dumps([{"role": "user", "parts": ["hi"]}, {"role": "user", "parts": ["hello again!"]}])
}

response = requests.post(url, data=data)
print(response.status_code)
print(response.text[:200])
