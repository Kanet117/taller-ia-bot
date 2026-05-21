import requests

url = "http://127.0.0.1:8000/chat"
data = {
    "text": "Hello",
    "history": '[{"role": "user", "parts": ["hi"]}, {"role": "model", "parts": ["hello!"]}]'
}

response = requests.post(url, data=data)
print(response.status_code)
print(response.text)
