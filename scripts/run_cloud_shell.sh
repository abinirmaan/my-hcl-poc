#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/validate_install.py
streamlit run app.py --server.address=0.0.0.0 --server.port=8080

