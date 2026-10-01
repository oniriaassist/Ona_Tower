from __future__ import annotations

from collections import Counter

from sqlalchemy.orm import Session

from app.data.cityview import CITYVIEW_UNITS
from app.database.models import AdminSetting
from app.schemas.cityview import CityViewInventory, CityViewStatus, CityViewUnit


CITYVIEW_STATUS_KEY = "cityview_unit_statuses"
VALID_STATUSES = {"available", "on_hold", "reserved", "sold"}


def _status_map(db: Session) -> dict[str, str]:
    record = db.get(AdminSetting, CITYVIEW_STATUS_KEY)
    if record is None or not isinstance(record.value, dict):
        return {}
    return {
        str(unit_code): str(status)
        for unit_code, status in record.value.items()
        if str(status) in VALID_STATUSES
    }


def cityview_inventory(db: Session) -> CityViewInventory:
    statuses = _status_map(db)
    units = [
        CityViewUnit(**seed, status=statuses.get(seed["unit_code"], "available"))
        for seed in CITYVIEW_UNITS
    ]
    counts = Counter(unit.status for unit in units)
    return CityViewInventory(
        units=units,
        total=len(units),
        counts={status: counts.get(status, 0) for status in ("available", "on_hold", "reserved", "sold")},
    )


def update_cityview_status(db: Session, unit_code: str, status: CityViewStatus) -> CityViewUnit | None:
    seed = next((item for item in CITYVIEW_UNITS if item["unit_code"] == unit_code), None)
    if seed is None:
        return None

    record = db.get(AdminSetting, CITYVIEW_STATUS_KEY)
    status_values = _status_map(db)
    status_values[unit_code] = status

    if record is None:
        record = AdminSetting(key=CITYVIEW_STATUS_KEY, value=status_values)
    else:
        record.value = status_values

    db.add(record)
    db.commit()
    db.refresh(record)
    return CityViewUnit(**seed, status=status)
