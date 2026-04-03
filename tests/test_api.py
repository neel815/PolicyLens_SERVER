import requests
import time
import json

start = time.time()
try:
    response = requests.post(
        'http://localhost:8000/api/analyze',
        files={'file': open('test_pdfs/SAMPLE_Health_Insurance_Policy.pdf', 'rb')},
        timeout=70
    )
    elapsed = time.time() - start
    print(f'✓ Response received in {elapsed:.1f} seconds')
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print('✓ SUCCESS!')
        print(f'Coverage Score: {data["data"]["coverage_score"]}/10')
        print(f'Covered Events: {len(data["data"]["covered_events"])} items')
        print(f'Exclusions: {len(data["data"]["exclusions"])} items')
        print(f'Risky Clauses: {len(data["data"]["risky_clauses"])} items')
    else:
        print(f'Error Status: {response.status_code}')
        print(f'Error: {response.text[:300]}')
except requests.Timeout:
    print('❌ API request timed out after 70 seconds')
except Exception as e:
    print(f'❌ Error: {str(e)[:200]}')
