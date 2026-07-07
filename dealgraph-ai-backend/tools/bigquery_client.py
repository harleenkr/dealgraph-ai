import json
import datetime
from google.cloud import bigquery
from google.auth.exceptions import DefaultCredentialsError

# Fallback wrapper for BigQuery
# Since the hackathon might be run locally without gcloud auth, we handle credentials gracefully
try:
    client = bigquery.Client()
    BQ_ENABLED = True
except DefaultCredentialsError:
    client = None
    BQ_ENABLED = False
except Exception as e:
    client = None
    BQ_ENABLED = False

# Update this to your real dataset in production
DATASET_ID = "dealgraph_ai"
TABLE_ID = "audit_events"

def stream_audit_to_bigquery(deal_id: str, agent_name: str, action: str, result: str):
    """
    Streams an audit log directly to Google BigQuery.
    Falls back to a successful simulated stream if credentials are not configured.
    """
    timestamp = datetime.datetime.utcnow().isoformat()
    row_to_insert = [
        {
            "timestamp": timestamp,
            "deal_id": deal_id,
            "agent_name": agent_name,
            "action": action,
            "result": result
        }
    ]

    if BQ_ENABLED and client:
        try:
            table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
            errors = client.insert_rows_json(table_ref, row_to_insert)
            if errors:
                print(f"[BigQuery] Error streaming row: {errors}")
            else:
                print(f"[BigQuery] Streamed event {action} to {DATASET_ID}.{TABLE_ID}")
        except Exception as e:
            print(f"[BigQuery] Connection Error: {str(e)}")
    else:
        # Smart Local Fallback for Demo
        print(f"[BigQuery Simulated] Streamed event {action} to {DATASET_ID}.{TABLE_ID} (Local mode)")
