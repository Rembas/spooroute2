# backend/app/domain/ports.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.domain.entities import JourneyRequest, Itinerary

class RealtimeProvider(ABC):
    @abstractmethod
    async def fetch_status(self) -> Dict[str, Any]: ...

class StaticGTFSRepository(ABC):
    @abstractmethod
    def stops_nearby(self, stop_id: str, radius_m: int) -> Dict[str, Any]: ...

class RoutePlannerPort(ABC):
    @abstractmethod
    def plan(self, req: JourneyRequest) -> List[Itinerary]: ...
