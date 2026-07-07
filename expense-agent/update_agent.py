import os
import vertexai
from vertexai.preview import reasoning_engines

os.environ["GOOGLE_CLOUD_PROJECT"] = "enduring-brace-499802-v7"
vertexai.init(project="enduring-brace-499802-v7", location="us-east1", staging_bucket="gs://enduring-brace-499802-v7-agent-bucket")

from app.agent import app as adk_app
from vertexai.agent_engines.templates.adk import AdkApp
from app.app_utils import services

print("Loading existing agent...")
remote_agent = reasoning_engines.ReasoningEngine("projects/217890036554/locations/us-east1/reasoningEngines/7921374347707547648")

print("Updating Reasoning Engine...")
rt = AdkApp(app=adk_app, session_service_builder=services.get_session_service, artifact_service_builder=services.get_artifact_service)

remote_agent.update(
    reasoning_engine=rt,
    requirements=[
        "google-adk[opentelemetry]==1.7.0",
        "google-cloud-aiplatform==1.82.0",
        "pydantic==2.10.6",
        "fastapi==0.115.11"
    ],
    extra_packages=["app"],
)
print("Update Complete.")
