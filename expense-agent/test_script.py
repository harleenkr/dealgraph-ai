import asyncio
from app.agent import root_agent, app
from google.adk.runners import InMemoryRunner
from google.genai import types

async def main():
    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(app_name="app", user_id="test")
    
    print("--- TEST 1: Auto-Approve (<100) ---")
    input_data = types.Content(role="user", parts=[types.Part.from_text(text='{"amount": 50.0, "description": "Lunch"}')])
    async for event in runner.run_async(user_id="test", session_id=session.id, new_message=input_data):
        if event.output is not None:
            print(f"Output: {event.output}")

    print("\n--- TEST 2: Review Needed (>=100) ---")
    input_data2 = types.Content(role="user", parts=[types.Part.from_text(text='{"amount": 150.0, "description": "Monitor"}')])
    async for event in runner.run_async(user_id="test", session_id=session.id, new_message=input_data2):
        if hasattr(event, 'interrupt_id') and event.interrupt_id:
            print(f"Paused for HITL, interrupt_id: {event.interrupt_id}")
            print("Simulating human response: approve")
            async for resume_event in runner.run_async(
                user_id="test", 
                session_id=session.id, 
                resume_inputs={event.interrupt_id: "approve"}
            ):
                if resume_event.output is not None:
                    print(f"Resume Output: {resume_event.output}")
        elif event.output is not None:
            print(f"Output: {event.output}")

if __name__ == "__main__":
    asyncio.run(main())
