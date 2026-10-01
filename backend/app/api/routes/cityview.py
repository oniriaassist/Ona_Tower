from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db_session
from app.schemas.cityview import CityViewInventory
from app.services.cityview_inventory import cityview_inventory


router = APIRouter(prefix="/cityview", tags=["City View"])


@router.get("/units", response_model=CityViewInventory)
async def list_cityview_units(db: Session = Depends(get_db_session)):
    return cityview_inventory(db)
