from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("Test 5: File field is empty string (no file selected in form)")
# Some frontend clients send an empty file object when no file is selected
response = client.post("/chat", data={"text": "hello"}, files={"file": ("", b"")})
print(response.status_code)
print(response.json())
