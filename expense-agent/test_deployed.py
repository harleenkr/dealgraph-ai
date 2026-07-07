import subprocess
import json

payload = {
    "newMessage": {
        "role": "user",
        "parts": [{"text": "I had a $150 client dinner"}]
    }
}

try:
    result = subprocess.run(
        ["agents-cli", "run", "--url", "https://us-east1-aiplatform.googleapis.com/v1/projects/217890036554/locations/us-east1/reasoningEngines/7921374347707547648", json.dumps(payload)],
        capture_output=True,
        text=True,
        env={"GOOGLE_CLOUD_PROJECT": "enduring-brace-499802-v7"}
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
except Exception as e:
    print(f"Error: {e}")
