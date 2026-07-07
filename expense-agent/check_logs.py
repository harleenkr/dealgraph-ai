import os
from google.cloud import logging

client = logging.Client(project="enduring-brace-499802-v7")
logger = client.logger("run.googleapis.com%2Fstderr") # Or we can just query the general logs

query = 'resource.type="aiplatform.googleapis.com/ReasoningEngine" AND resource.labels.reasoning_engine_id="7921374347707547648"'
for entry in client.list_entries(filter_=query, max_results=20, order_by=logging.DESCENDING):
    print(f"[{entry.timestamp}] {entry.severity}: {entry.payload}")
