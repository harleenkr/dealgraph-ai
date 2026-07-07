import subprocess
import uuid

def test_human_in_the_loop():
    # Generate a unique session ID to maintain state across the two turns
    session_id = str(uuid.uuid4())
    print(f"Starting multi-turn evaluation for Session ID: {session_id}\n")

    url = "https://us-east1-aiplatform.googleapis.com/v1beta1/projects/217890036554/locations/us-east1/reasoningEngines/7921374347707547648"
    
    # ---------------------------------------------------------
    # TURN 1: Submit the $150 expense claim
    # ---------------------------------------------------------
    print("==================================================")
    print("[TURN 1] Submitting $150 expense (expecting pause)")
    print("==================================================")
    
    payload = '{"amount": 150.0, "description": "Client dinner"}'
    cmd1 = f"agents-cli run '{payload}' --url {url} --mode adk --session-id {session_id}"
    
    res1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True)
    print(res1.stdout)
    
    # ---------------------------------------------------------
    # TURN 2: Manager provides the review decision
    # ---------------------------------------------------------
    print("\n==================================================")
    print("[TURN 2] Manager submitting 'approve' decision")
    print("==================================================")
    
    # To resume a specific interrupt_id ('manager_review'), we pass a JSON dict
    decision = '{"manager_review": "approve"}'
    cmd2 = f"agents-cli run '{decision}' --url {url} --mode adk --session-id {session_id}"
    
    res2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
    print(res2.stdout)
    
    # Verify the output
    final_output = res2.stdout
    assert "approved" in final_output.lower(), f"Expected the expense to be approved by manager, got: {final_output}"
    print("\n✅ Multi-turn Evaluation Passed: The agent successfully paused and resumed the session!")

if __name__ == "__main__":
    test_human_in_the_loop()
