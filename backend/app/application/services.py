# backend/app/application/services.py
from typing import Any, Dict, Optional
from app.settings import settings
from app.adapters.repositories import FixtureRepository
from app.adapters.alternatives import SimpleAlternativeSuggester

DEMO_SCENARIO = "normal"  # normal|heavy

class JourneyRadarService:
    def __init__(self, repo: FixtureRepository, suggester: SimpleAlternativeSuggester):
        self.repo = repo
        self.suggester = suggester

    async def get_status(self)->Dict[str,Any]:
        if settings.demo_mode:
            fname = "demo_delays.json" if DEMO_SCENARIO=="normal" else "demo_delays_heavy.json"
            return self.repo.load_fixture(fname)
        return {"lines":[]}

    async def get_alerts(self) -> Dict[str, Any]:
        if settings.demo_mode:
            return self.repo.load_fixture("demo_alerts.json")
        return {"alerts": []}

    async def get_alternatives(self, from_stop: str, radius_m: int, window_min: int) -> Dict[str, Any]:
        if settings.demo_mode:
            # Per-stop fixture se presente; fallback al file generico
            per_stop = f"demo_alternatives_{from_stop}.json"
            data: Optional[Dict[str, Any]] = None
            # Usa la funzione se esiste, altrimenti fallback diretto
            if hasattr(self.repo, "load_fixture_if_exists"):
                data = self.repo.load_fixture_if_exists(per_stop)  # type: ignore[attr-defined]
            if not data:
                data = self.repo.load_fixture("demo_alternatives.json")
                data["from_stop"] = from_stop
            return data
        # Modalità non demo: usa il suggester placeholder
        return self.suggester.suggest(from_stop, radius_m, window_min)

def get_service() -> "JourneyRadarService":
    """Factory usata dai Depends(...) negli endpoint."""
    repo = FixtureRepository()
    suggester = SimpleAlternativeSuggester()
    return JourneyRadarService(repo, suggester)
