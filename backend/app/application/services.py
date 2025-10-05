# backend/app/application/services.py
from typing import Any, Dict, Optional, List
from app.settings import settings
from app.adapters.repositories import FixtureRepository
from app.adapters.alternatives import SimpleAlternativeSuggester
from app.adapters.router.csa_planner import CsaRoutePlanner
from app.domain.entities import JourneyRequest, Itinerary

# demo scenario toggle (usato altrove se implementi switcher)
DEMO_SCENARIO = "normal"  # normal|heavy

class JourneyRadarService:
    def __init__(self,
                 repo: FixtureRepository,
                 suggester: SimpleAlternativeSuggester,
                 planner: Optional[CsaRoutePlanner] = None):
        self.repo = repo
        self.suggester = suggester
        self.planner = planner or CsaRoutePlanner()

    async def get_status(self) -> Dict[str, Any]:
        if settings.demo_mode:
            fname = "demo_delays.json" if DEMO_SCENARIO == "normal" else "demo_delays_heavy.json"
            return self.repo.load_fixture(fname)
        return {"lines": []}

    async def get_alerts(self) -> Dict[str, Any]:
        if settings.demo_mode:
            return self.repo.load_fixture("demo_alerts.json")
        return {"alerts": []}

    async def get_alternatives(self, from_stop: str, radius_m: int, window_min: int) -> Dict[str, Any]:
        if settings.demo_mode:
            per_stop = f"demo_alternatives_{from_stop}.json"
            data = getattr(self.repo, "load_fixture_if_exists", lambda _: None)(per_stop)
            if not data:
                data = self.repo.load_fixture("demo_alternatives.json")
                data["from_stop"] = from_stop
            return data
        return self.suggester.suggest(from_stop, radius_m, window_min)

    async def plan(self, from_stop: str, to_stop: str, depart_at: int) -> Dict[str, Any]:
        """
        Always try planner; if DB missing or no path, demo fallback inside the planner returns a synthetic itinerary.
        """
        req = JourneyRequest(from_stop=from_stop, to_stop=to_stop, depart_at=depart_at)
        itins: List[Itinerary] = self.planner.plan(req)
        out = []
        for it in itins:
            out.append({
                "total_time": it.total_time,
                "transfers": it.transfers,
                "legs": [
                    {
                        "mode": lg.mode,
                        "from_stop": lg.from_stop,
                        "to_stop": lg.to_stop,
                        "dep_time": lg.dep_time,
                        "arr_time": lg.arr_time,
                        "route_id": lg.route_id,
                        "trip_id": lg.trip_id,
                        "distance_m": lg.distance_m,
                    } for lg in it.legs
                ]
            })
        return {"itineraries": out}

def get_service() -> "JourneyRadarService":
    repo = FixtureRepository()
    suggester = SimpleAlternativeSuggester()
    planner = CsaRoutePlanner(settings.gtfs_sqlite_path)
    return JourneyRadarService(repo, suggester, planner)
