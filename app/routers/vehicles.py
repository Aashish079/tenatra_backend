from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from app.database import SessionDependency as DBSession
from app.models import EvCar
from app.security import BearerAuthUser

vehicles_router = APIRouter()


class EvCarRequest(BaseModel):
    make: str
    model: str
    year: Optional[str] = None
    plugType: Optional[str] = None
    batteryKwh: Optional[str] = None
    rangeKm: Optional[str] = None


class EvCarResponse(BaseModel):
    make: str
    model: str
    year: Optional[str] = None
    plugType: Optional[str] = None
    batteryKwh: Optional[str] = None
    rangeKm: Optional[str] = None


@vehicles_router.get("/vehicles", response_model=Optional[EvCarResponse])
def get_vehicle(user: BearerAuthUser, db: DBSession):
    """Return the authenticated user's EV vehicle if present."""
    ev = db.exec(select(EvCar).where(EvCar.user_id == user.user_id)).first()
    if not ev:
        return None
    return EvCarResponse(
        make=ev.make,
        model=ev.model,
        year=ev.year,
        plugType=ev.plug_type,
        batteryKwh=ev.battery_kwh,
        rangeKm=ev.range_km,
    )


@vehicles_router.put("/vehicles", status_code=status.HTTP_204_NO_CONTENT)
def upsert_vehicle(payload: EvCarRequest, user: BearerAuthUser, db: DBSession):
    """Create or update the authenticated user's EV vehicle."""
    ev = db.exec(select(EvCar).where(EvCar.user_id == user.user_id)).first()
    if not ev:
        ev = EvCar(
            user_id=user.user_id,
            make=payload.make,
            model=payload.model,
            year=payload.year,
            plug_type=payload.plugType,
            battery_kwh=payload.batteryKwh,
            range_km=payload.rangeKm,
        )
        db.add(ev)
    else:
        ev.make = payload.make
        ev.model = payload.model
        ev.year = payload.year
        ev.plug_type = payload.plugType
        ev.battery_kwh = payload.batteryKwh
        ev.range_km = payload.rangeKm
        db.add(ev)

    db.commit()
    return None
