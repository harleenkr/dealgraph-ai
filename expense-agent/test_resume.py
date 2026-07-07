import asyncio
import os
from vertexai.agent_engines.templates.adk import AdkApp
from app.agent import app as adk_app
from google.adk.sessions.in_memory_session_service import InMemorySessionService

os.environ["GOOGLE_CLOUD_PROJECT"] = "enduring-brace-499802-v7"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-east1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

runtime = AdkApp(
    app=adk_app,
    session_service_builder=lambda **k: InMemorySessionService(),
    artifact_service_builder=lambda **k: None,
)
runtime.set_up()

async def main():
    # 1. Start session
    events1 = []
    session_id = "test-session"
    print("--- Request 1 ---")
    async for e in runtime.async_stream_query(
        session_id=session_id,
        message={"parts": [{"text": "I had a $150 client dinner"}], "role": "user"},
        user_id="user123",
    ):
        print(e)
        events1.append(e)
    
    print("\n--- Request 2 ---")
    # 2. Resume session
    events2 = []
    async for e in runtime.async_stream_query(
        session_id=session_id,
        message={"parts": [{"text": "Approved"}], "role": "user"},
        user_id="user123",
    ):
        print(e)
        events2.append(e)

if __name__ == "__main__":
    asyncio.run(main())
