import os
from typing import List, Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from google.adk.sessions.vertex_ai_session_service import VertexAiSessionService
from vertexai.preview import reasoning_engines

app = FastAPI(title="Manager Dashboard")

# Ensure static directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), "static"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "enduring-brace-499802-v7")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-east1")
AGENT_RUNTIME_ID = os.environ.get("AGENT_RUNTIME_ID", "projects/217890036554/locations/us-east1/reasoningEngines/7921374347707547648")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(os.path.dirname(__file__), "static", "index.html"), "r") as f:
        return f.read()

@app.get("/api/pending")
async def get_pending_approvals():
    try:
        service = VertexAiSessionService(
            project=PROJECT_ID,
            location=LOCATION
        )
        
        # Note: the list_sessions method might require specific arguments or return objects
        # We assume it returns an iterable of session objects or dictionaries containing session_id
        sessions = await service.list_sessions(app_name=AGENT_RUNTIME_ID)
        
        pending_requests = []
        for session_obj in sessions:
            # list_sessions returns a list of session_id strings usually, or objects
            session_id = session_obj if isinstance(session_obj, str) else session_obj.get("session_id") if isinstance(session_obj, dict) else getattr(session_obj, "session_id", None)
            if not session_id:
                continue
                
            session_data = await service.get_session(session_id)
            if not session_data:
                continue
                
            history = getattr(session_data, "history", [])
            if not history:
                continue
                
            # Keep track of function calls and responses
            function_calls = {}
            function_responses = set()
            
            # Extract content from Content objects
            for item in history:
                if hasattr(item, "parts"):
                    for part in item.parts:
                        if hasattr(part, "function_call") and getattr(part, "function_call", None):
                            if part.function_call.name == "adk_request_input":
                                # Save details
                                call_id = part.function_call.id
                                args = getattr(part.function_call, "args", {})
                                if hasattr(args, "get"):
                                    function_calls[call_id] = {
                                        "id": call_id,
                                        "description": args.get("description", ""),
                                        "amount": args.get("amount", 0) # if available
                                    }
                                elif hasattr(args, "fields"):
                                    # Handle struct fields
                                    fields = args.fields
                                    function_calls[call_id] = {
                                        "id": call_id,
                                        "description": getattr(fields.get("description"), "string_value", ""),
                                        "amount": getattr(fields.get("amount"), "number_value", 0)
                                    }
                                else:
                                    # dict
                                    function_calls[call_id] = {
                                        "id": call_id,
                                        "description": args.get("description", "") if isinstance(args, dict) else str(args)
                                    }
                        
                        if hasattr(part, "function_response") and getattr(part, "function_response", None):
                            if part.function_response.name == "adk_request_input":
                                function_responses.add(part.function_response.id)
            
            # Find unresolved ones
            for call_id, call_data in function_calls.items():
                if call_id not in function_responses:
                    pending_requests.append({
                        "session_id": session_id,
                        "interrupt_id": call_id,
                        "details": call_data
                    })
                    
        return JSONResponse(content={"pending": pending_requests})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)


import base64
import json

@app.post("/api/pubsub")
async def pubsub_webhook(request: Request):
    try:
        body = await request.json()
        if not body or "message" not in body or "data" not in body["message"]:
            return JSONResponse(content={"error": "Invalid Pub/Sub payload"}, status_code=400)
            
        data_b64 = body["message"]["data"]
        data_str = base64.b64decode(data_b64).decode("utf-8")
        payload = json.loads(data_str)
        
        # Expecting payload: {"input": {"message": "..."}}
        message_str = payload.get("input", {}).get("message")
        if not message_str:
            return JSONResponse(content={"error": "No message found in payload"}, status_code=400)
            
        message = json.loads(message_str)
        
        remote_app = reasoning_engines.ReasoningEngine(AGENT_RUNTIME_ID)
        # We need a proper user_id for Vertex AI Agent Engine.
        # User ID must strictly be 'default-user' so it shows up in dashboard.
        response = remote_app.query(message=message, user_id="default-user")
        
        return JSONResponse(content={"success": True, "response": str(response)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return 200 so Pub/Sub doesn't infinitely retry on unrecoverable errors
        return JSONResponse(content={"error": str(e)}, status_code=200)


@app.post("/api/action/{session_id}")
async def take_action(session_id: str, request: Request):
    try:
        data = await request.json()
        interrupt_id = data.get("interrupt_id")
        approved = data.get("approved", False)
        
        remote_app = reasoning_engines.ReasoningEngine(AGENT_RUNTIME_ID)
        
        # Pass exactly the format expected by ADK
        message = {
            "role": "user",
            "parts": [
                {
                    "function_response": {
                        "id": interrupt_id,
                        "name": "adk_request_input",
                        "response": {"decision": "approved" if approved else "rejected"}
                    }
                }
            ]
        }
        
        # User ID must strictly be 'default-user' to avoid mismatch
        response = remote_app.query(message=message, user_id="default-user", session_id=session_id)
        
        # if the query responds with something, convert to string
        return JSONResponse(content={"success": True, "response": str(response)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
