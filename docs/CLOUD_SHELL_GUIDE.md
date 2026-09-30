# Google Cloud Shell guide

## 1. Upload and extract

Upload `AI_Assisted_Test_Case_Writing_POC.zip` to Cloud Shell, then run:

```bash
unzip AI_Assisted_Test_Case_Writing_POC.zip
cd ai_test_case_poc
chmod +x scripts/run_cloud_shell.sh
./scripts/run_cloud_shell.sh
```

Open **Web Preview → Preview on port 8080**.

## 2. Safe client-demo mode

Keep **Demo Engine** selected. It is deterministic, requires no API call, and demonstrates the complete workflow.

## 3. Vertex AI Gemini mode

Select or create a Google Cloud project with billing, then run:

```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable aiplatform.googleapis.com
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GEMINI_MODEL="gemini-2.5-flash"
export AI_MODE="vertex"
streamlit run app.py --server.address=0.0.0.0 --server.port=8080
```

Your user or service account needs permission to invoke Vertex AI models. If the model call fails during a meeting, switch back to **Demo Engine** from the sidebar.

## 4. Troubleshooting

- Blank preview: confirm Streamlit is using port 8080 and reopen Web Preview.
- Vertex permission error: confirm the project, billing, API enablement, region, and IAM access.
- Package installation issue: recreate `.venv`, then rerun the script.
- Session lost: Cloud Shell is ephemeral. Export test suites before ending the session.

## 5. Production path

For the next phase, containerize with the supplied Dockerfile and deploy to Cloud Run. Add identity, a persistent database, Secret Manager, logging, model monitoring, and approved Jira or TestRail integration.

