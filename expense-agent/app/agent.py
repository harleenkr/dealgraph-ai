# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import google.auth
from pydantic import BaseModel

from google.adk.workflow import Workflow, node
from google.adk.agents.context import Context
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.apps import App, ResumabilityConfig
from google.genai import types
from google.genai import Client
import json

try:
    _, project_id = google.auth.default()
    if project_id:
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
except Exception:
    pass

os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


class ExpenseClaim(BaseModel):
    amount: float
    description: str


class ExpenseOutcome(BaseModel):
    status: str
    amount: float
    reason: str


@node
def extractor(node_input: str) -> Event:
    """Extracts expense claim from natural language."""
    genai_client = Client(vertexai=True, project="enduring-brace-499802-v7", location="us-east1")
    prompt = f"Extract the expense amount and description from this text. Text: {node_input}"
    
    response = genai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExpenseClaim,
            temperature=0.1
        ),
    )
    
    claim_dict = json.loads(response.text)
    claim = ExpenseClaim(**claim_dict)
    
    return Event(output=claim)

@node
def classifier(node_input: ExpenseClaim) -> Event:
    """Routes the expense claim based on amount."""
    if node_input.amount < 100:
        return Event(output=node_input, route="auto_approve")
    else:
        return Event(output=node_input, route="review")


@node
def auto_approve(node_input: ExpenseClaim) -> Event:
    """Automatically approves standard claims."""
    outcome = ExpenseOutcome(status="approved", amount=node_input.amount, reason="auto-approved (<$100)")
    return Event(
        output=outcome,
        content=types.Content(role="model", parts=[types.Part.from_text(text=f"Expense of ${node_input.amount} auto-approved.")])
    )


@node
async def review_agent(ctx: Context, node_input: ExpenseClaim) -> Event:
    """Triggers human-in-the-loop review for larger expenses."""
    
    approval_input = ctx.resume_inputs.get("approval_manager")
    
    if not approval_input:
        yield Event(
            content=types.Content(role="model", parts=[types.Part.from_text(text=f"Expense of ${node_input.amount} requires manager approval. Please review.")]),
            pause=RequestInput(id="approval_manager", description="Provide manager approval decision")
        )
        return

    if hasattr(approval_input, "get"):
        decision = approval_input.get("decision", "rejected")
    elif isinstance(approval_input, str):
        decision = approval_input.lower()
    elif hasattr(approval_input, "parts") and approval_input.parts:
        decision = approval_input.parts[0].text.lower()
    else:
        decision = "rejected"
    outcome = ExpenseOutcome(status=decision, amount=node_input.amount, reason="manager reviewed")
    
    yield Event(
        output=outcome,
        content=types.Content(role="model", parts=[types.Part.from_text(text=f"Expense of ${node_input.amount} was {decision} after manual review.")])
    )


from google.adk.workflow import Edge, START
from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin

# Define the workflow graph
root_agent = Workflow(
    name="expense_workflow",
    edges=[
        Edge(from_node=START, to_node=extractor),
        Edge(from_node=extractor, to_node=classifier),
        Edge(from_node=classifier, to_node=auto_approve, route="auto_approve"),
        Edge(from_node=classifier, to_node=review_agent, route="review"),
    ],
    input_schema=str,
    output_schema=ExpenseOutcome,
)

app = App(
    root_agent=root_agent,
    name="expense_processor",
    resumability_config=ResumabilityConfig(enabled=True),
    plugins=[
        BigQueryAgentAnalyticsPlugin(
            project_id=os.environ.get("GOOGLE_CLOUD_PROJECT", "enduring-brace-499802-v7"),
            dataset_id=os.environ.get("BQ_ANALYTICS_DATASET_ID", "adk_agent_analytics"),
            logging_enabled=True,
        )
    ]
)
