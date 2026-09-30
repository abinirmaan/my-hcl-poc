# AI-Assisted Test Case Writing POC

An end-to-end Streamlit proof of concept that converts software requirements into structured, traceable test cases. It supports Google Vertex AI Gemini and includes a deterministic demo engine so a client presentation never depends on live model access.

## What the POC demonstrates

- Requirement input by paste or `.txt`, `.md`, `.csv`, or `.json` upload
- Requirement parsing and ambiguity detection
- Functional, negative, boundary, validation, security, and regression cases
- Requirement-to-test traceability and coverage scoring
- Duplicate and quality checks
- QA reviewer actions: accept, edit, reject, and regenerate
- Excel, CSV, and JSON export
- Session audit trail and KPI dashboard
- Vertex AI Gemini mode plus reliable demo mode

## Folder structure

```text
ai_test_case_poc/
├── app.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── .streamlit/config.toml
├── data/sample_login_requirement.txt
├── presentation/AI_Assisted_Test_Case_Writing_POC_Architecture.pptx
├── docs/
│   ├── CLOUD_SHELL_GUIDE.md
│   └── CLIENT_DEMO_GUIDE.md
├── scripts/
│   ├── run_cloud_shell.sh
│   └── validate_install.py
├── src/
│   ├── config.py
│   ├── exports.py
│   ├── generator.py
│   ├── llm_client.py
│   ├── models.py
│   ├── parser.py
│   ├── prompts.py
│   ├── quality.py
│   └── sample_data.py
└── tests/
    └── test_core.py
```

## Fast start in Google Cloud Shell

```bash
unzip AI_Assisted_Test_Case_Writing_POC.zip
cd ai_test_case_poc
chmod +x scripts/run_cloud_shell.sh
./scripts/run_cloud_shell.sh
```

Open **Web Preview → Preview on port 8080**.

The application starts in **Demo Engine** mode. To use Vertex AI, follow [docs/CLOUD_SHELL_GUIDE.md](docs/CLOUD_SHELL_GUIDE.md).

## Local start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## POC boundary

This code is designed for a controlled client demonstration. Production deployment should add enterprise identity, persistent encrypted storage, formal retention rules, model monitoring, prompt/version governance, and approved Jira or TestRail connectors.
# sougata_hcl_poc
