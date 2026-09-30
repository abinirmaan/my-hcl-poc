from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    ai_mode: str = os.getenv("AI_MODE", "demo").lower()
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    model_name: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    @property
    def vertex_ready(self) -> bool:
        return bool(self.project_id and self.location and self.model_name)


SETTINGS = Settings()

