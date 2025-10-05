import json, os
from typing import Dict, Any, Optional

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")

class FixtureRepository:
    def load_fixture(self, filename: str) -> Dict[str, Any]:
        path = os.path.join(FIXTURE_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_fixture_if_exists(self, filename: str) -> Optional[Dict[str, Any]]:
        path = os.path.join(FIXTURE_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
