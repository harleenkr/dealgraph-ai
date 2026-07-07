import asyncio
import json
import os
import sys
from dotenv import load_dotenv

from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from google.adk.events.request_input import RequestInput
from vertexai._genai.types.common import EvaluationDataset, EvalCase

from expense_agent.agent import root_agent

load_dotenv()

app_config = App(name="ambient_expense", root_agent=root_agent)
runner = InMemoryRunner(app=app_config)

async def main():
    dataset_path = "tests/eval/datasets/basic-dataset.json"
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}")
        sys.exit(1)

    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    os.makedirs("artifacts/traces", exist_ok=True)
    
    traces = []
    print(f"Generating traces for {len(dataset)} scenarios...")
    
    for row in dataset:
        prompt = row["prompt"]
        expected = row.get("expected_decision", "")
        print(f"\nProcessing scenario: {row['id']} (Expected: {expected})")
        
        session = await runner.session_service.create_session(
            app_name=app_config.name, 
            user_id="evaluator"
        )
        
        events_log = []
        final_output = None
        
        # Run workflow
        async for event in runner.run_async(
            user_id="evaluator",
            session_id=session.id,
            new_message=Content(role="user", parts=[Part.from_text(text=prompt)])
        ):
            if isinstance(event, RequestInput):
                print("  -> Paused for human input, resuming automatically...")
                events_log.append({"type": "RequestInput", "description": "Paused for human review"})
                
                async for res_event in runner.resume_async(
                    user_id="evaluator",
                    session_id=session.id,
                    new_inputs="APPROVED (Automated trace test)",
                ):
                    out_str = str(res_event.output)
                    events_log.append({"type": "Event", "output": out_str})
                    final_output = res_event.output
                    print(f"  -> {out_str}")
            else:
                out_str = str(event.output)
                events_log.append({"type": "Event", "output": out_str})
                final_output = event.output
                print(f"  -> {out_str}")
                
        traces.append(EvalCase(
            eval_case_id=row.get("id", ""),
            prompt=Content(role="user", parts=[Part.from_text(text=prompt)]),
            responses=[Content(role="model", parts=[Part.from_text(text=str(final_output))])],
            system_instruction=Content(role="system", parts=[Part.from_text(text=json.dumps({"events": events_log}))])
        ))
        
    ds = EvaluationDataset(eval_cases=traces)
    traces_path = "artifacts/traces/generated_traces.json"
    with open(traces_path, "w") as f:
        f.write(ds.model_dump_json(indent=2))
        
    print(f"\nSuccessfully generated traces and saved to {traces_path}")
        
if __name__ == "__main__":
    asyncio.run(main())
