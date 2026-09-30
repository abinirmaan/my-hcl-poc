from __future__ import annotations

import json
import re
from google import genai
from google.genai import types
from .config import SETTINGS


def generate_json(prompt: str) -> tuple[dict, str]:
    if not SETTINGS.vertex_ready:
        raise RuntimeError("Vertex AI configuration is incomplete. Set GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION.")
    client = genai.Client(vertexai=True, project=SETTINGS.project_id, location=SETTINGS.location)
    response = client.models.generate_content(
        model=SETTINGS.model_name,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2, response_mime_type="application/json"),
    )
    text = response.text or ""
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("The model did not return a JSON object.")
    return json.loads(match.group(0)), SETTINGS.model_name

