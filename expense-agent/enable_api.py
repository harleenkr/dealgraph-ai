import google.auth
from google.auth.transport.requests import AuthorizedSession

def enable_api():
    credentials, project = google.auth.default()
    authed_session = AuthorizedSession(credentials)
    
    apis = [
        "aiplatform.googleapis.com",
        "run.googleapis.com",
        "pubsub.googleapis.com",
        "cloudbuild.googleapis.com"
    ]
    
    for api in apis:
        print(f"Enabling {api}...")
        url = f"https://serviceusage.googleapis.com/v1/projects/enduring-brace-499802-v7/services/{api}:enable"
        response = authed_session.post(url)
        print(f"Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    enable_api()
