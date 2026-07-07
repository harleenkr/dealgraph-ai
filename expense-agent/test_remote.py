import os
import vertexai
from vertexai.preview import reasoning_engines
import json

os.environ["GOOGLE_CLOUD_PROJECT"] = "enduring-brace-499802-v7"
vertexai.init(project="enduring-brace-499802-v7", location="us-east1")

print("Loading remote agent...")
remote_agent = reasoning_engines.ReasoningEngine("projects/217890036554/locations/us-east1/reasoningEngines/7921374347707547648")

print("\n--- Test Case 1: Standard meal expense of $50 (Auto-approval) ---")
payload1 = {"amount": 50.0, "description": "Standard meal expense"}
response1 = remote_agent.query(input=json.dumps(payload1))
print("Response:", response1)

print("\n--- Test Case 2: Client dinner expense of $150 (Human-in-the-loop pause) ---")
payload2 = {"amount": 150.0, "description": "Client dinner"}
response2 = remote_agent.query(input=json.dumps(payload2))
print("Response:", response2)
