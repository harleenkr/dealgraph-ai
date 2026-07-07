import logging
import base64
from fastapi import FastAPI, Request
from google.adk.apps import App
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner

from expense_agent.agent import root_agent

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv()

# Use standard Python logging for console logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the app
app_config = App(name="ambient_expense", root_agent=root_agent)
runner = InMemoryRunner(app=app_config)

api = FastAPI()

@api.post("/")
async def handle_pubsub(request: Request):
    try:
        envelope = await request.json()
    except Exception:
        return "Bad Request: invalid JSON", 400
        
    if not envelope:
        return "Bad Request: no Pub/Sub message received", 400
        
    message = envelope.get("message", {})
    subscription = envelope.get("subscription", "default")
    
    # Normalize subscription path from "projects/foo/subscriptions/sub-name" to "sub-name"
    if "/" in subscription:
        subscription = subscription.split("/")[-1]
        
    data = message.get("data")
    if not data:
        return "Bad Request: no data in message", 400
        
    logger.info(f"Received message from subscription {subscription}")
    
    # Create a session to track this specific execution
    session = await runner.session_service.create_session(
        app_name=app_config.name, 
        user_id="pubsub_trigger"
    )
    
    logger.info(f"Starting workflow for session {session.id}")
    
    # Run the workflow. Wrap the raw base64 string in a Content object.
    from google.genai.types import Content, Part
    
    async for event in runner.run_async(
        user_id="pubsub_trigger",
        session_id=session.id,
        new_message=Content(role="user", parts=[Part.from_text(text=data)])
    ):
        if event.output:
            logger.info(f"Workflow output: {event.output}")
            
    return "OK", 200
