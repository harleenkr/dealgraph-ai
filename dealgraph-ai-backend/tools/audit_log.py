import datetime
from tools.bigquery_client import stream_audit_to_bigquery

def log_audit_event(deal_id: str, agent_name: str, action: str, result: str = "") -> dict:
    """Creates audit log entries and streams them to BigQuery."""
    timestamp = datetime.datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "deal_id": deal_id,
        "agent_name": agent_name,
        "action": action,
        "result": result
    }
    
    # 1. Standard stdout logging
    print(f"AUDIT [{timestamp}] {deal_id} | {agent_name} | {action} | {result}")
    
    # 2. Stream to Google BigQuery
    stream_audit_to_bigquery(deal_id, agent_name, action, result)
    
    return log_entry
