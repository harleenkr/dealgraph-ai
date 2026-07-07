import json
import urllib.request
import google.auth
from google.auth.transport.requests import Request

credentials, project = google.auth.default()
credentials.refresh(Request())

url = "https://us-east1-aiplatform.googleapis.com/v1beta1/projects/217890036554/locations/us-east1/reasoningEngines/7921374347707547648:query"

payload = {
    "input": {
        "newMessage": {
            "role": "user",
            "parts": [{"text": "I had a $150 client dinner"}]
        }
    }
}

req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'))
req.add_header('Authorization', f'Bearer {credentials.token}')
req.add_header('Content-Type', 'application/json')

try:
    response = urllib.request.urlopen(req)
    print("SUCCESS:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"ERROR: {e}")
