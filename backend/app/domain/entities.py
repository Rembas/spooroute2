from dataclasses import dataclass
from typing import Optional, List

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