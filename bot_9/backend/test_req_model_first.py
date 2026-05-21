import requests
import json

url = "http://127.0.0.1:8000/chat"
data = {
    "text": "Hello",
    "history": json.dumps([{"role": "model", "parts": ["Hello! I am your assistant."]}])
}

response = requests.post(url, data=data)
print(response.status_code)
print(response.text[:200])
