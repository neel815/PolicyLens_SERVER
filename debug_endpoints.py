import requests
import json

url = 'http://localhost:8000/api/auth/register'
data = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'testpass123',
    'full_name': 'Test User'
}

print(f"Testing GET /openapi.json...")
r = requests.get('http://localhost:8000/openapi.json')
paths = list(r.json().get('paths', {}).keys())
print(f"Paths in OpenAPI: {paths}")

print(f"\nTesting POST {url}...")
r = requests.post(url, json=data, timeout=5)
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")
