import os
import vertexai
from vertexai.preview import reasoning_engines

os.environ["GOOGLE_CLOUD_PROJECT"] = "enduring-brace-499802-v7"
vertexai.init(project="enduring-brace-499802-v7", location="us-east1")

# The agent deployment script
from app.agent import app as adk_app
from vertexai.agent_engines.templates.adk import AdkApp
from app.app_utils import services

print("Deploying Reasoning Engine...")
rt = AdkApp(app=adk_app, session_service_builder=services.get_session_service, artifact_service_builder=services.get_artifact_service)

remote_agent = reasoning_engines.ReasoningEngine.create(
    rt,
    requirements=[
        "google-adk[opentelemetry]==1.7.0",
        "google-cloud-aiplatform==1.82.0",
        "pydantic==2.10.6",
        "fastapi==0.115.11"
    ],
    extra_packages=["app"],
    display_name="Expense Agent",
)
print("Deployment Complete.")
print(remote_agent.resource_name)
