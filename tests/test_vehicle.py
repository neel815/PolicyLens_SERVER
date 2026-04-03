import requests
import json

response = requests.post(
    'http://localhost:8000/api/analyze',
    files={'file': open('test_pdfs/SAMPLE_Vehicle_Insurance_Policy.pdf', 'rb')},
    timeout=70
)

data = response.json()
print(f'✓ Response received')
print(f'Status Code: {response.status_code}')
if response.status_code == 200:
    print(f'✓ Vehicle Insurance Policy')
    result = data['data']
    print(f'Coverage Score: {result["coverage_score"]}/10')
    print(f'Covered Events: {result["covered_events"]}')
    print(f'Exclusions: {result["exclusions"]}')
else:
    print(f'Error: {json.dumps(data, indent=2)}')
