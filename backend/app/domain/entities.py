# backend/app/domain/entities.py
from dataclasses import dataclass, field
from typing import Optional, List

# --- già presenti (status / alt / alert) ---
@dataclass
class RouteStatus:
    route_id: str
    status: str  # on_time | delayed | alert
    delay_min: int = 0

@dataclass
class Alternative:
    route_id: str
    stop_id: str
    stop_name: str
    depart_in_min: int
    distance_m: int
    changes: int = 0

@dataclass
class ServiceAlert:
    id: str
    severity: str
    text: str
    route_ids: Optional[List[str]] = None

# --- Planner CSA ---

@dataclass
class JourneyRequest:
    from_stop: str
    to_stop: str
    depart_at: int            # seconds since midnight
    max_transfers: int = 3
    window_sec: int = 90 * 60 # how far we scan

@dataclass
class Connection:
    dep_time: int
    arr_time: int
    from_stop: str
    to_stop: str
    trip_id: str
    route_id: str

@dataclass
class Leg:
    mode: str                 # "walk" | "transit"
    from_stop: str
    to_stop: str
    dep_time: int
    arr_time: int
    route_id: Optional[str] = None
    trip_id: Optional[str] = None
    distance_m: Optional[int] = None   # only for walk

@dataclass
class Itinerary:
    legs: List[Leg] = field(default_factory=list)

    @property
    def total_time(self) -> int:
        if not self.legs:
            return 0
        return self.legs[-1].arr_time - self.legs[0].dep_time

    @property
    def transfers(self) -> int:
        tr = 0
        last_trip = None
        for lg in self.legs:
            if lg.mode == "transit":
                if last_trip is not None and lg.trip_id != last_trip:
                    tr += 1
                last_trip = lg.trip_id
        return tr
