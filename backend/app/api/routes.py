from fastapi import APIRouter, Depends, Query
from app.application.services import JourneyRadarService, get_service
from app.application.services import DEMO_SCENARIO

router = APIRouter()

@router.get("/status")
async def status(svc: JourneyRadarService = Depends(get_service)):
    return await svc.get_status()

@router.get("/alerts")
async def alerts(svc: JourneyRadarService = Depends(get_service)):
    return await svc.get_alerts()

@router.get("/alternatives")
async def alternatives(from_stop: str, radius_m: int = 400, window_min: int = 20, svc: JourneyRadarService = Depends(get_service)):
    return await svc.get_alternatives(from_stop, radius_m, window_min)

@router.get("/bulletins")
async def bulletins(svc: JourneyRadarService = Depends(get_service)):
    # in demo serviamo il file; in reale potresti leggere da DB
    return {"bulletins": svc.repo.load_fixture("demo_bulletins.json").get("bulletins", [])}

@router.post("/_demo/scenario")
async def set_scenario(s: str):
    global DEMO_SCENARIO
    if s in ("normal","heavy"):
        DEMO_SCENARIO = s
    return {"scenario": DEMO_SCENARIO}


@router.get("/plan")
async def plan(
    from_stop: str = Query(...),
    to_stop: str = Query(...),
    depart_at: int = Query(..., description="seconds since midnight"),
    svc: JourneyRadarService = Depends(get_service)
):
    return await svc.plan(from_stop, to_stop, depart_at)
