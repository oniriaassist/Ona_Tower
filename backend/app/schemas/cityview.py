from typing import Literal

from pydantic import BaseModel


CityViewStatus = Literal["available", "on_hold", "reserved", "sold"]


class CityViewUnit(BaseModel):
    unit_code: str
    tower: str
    floor_number: int | None
    floor_label: str
    bedrooms: int
    residence_type: str
    view: str
    status: CityViewStatus = "available"
    suite_area_sqm: int
    balcony_area_sqm: int
    total_area_sqm: int
    floor_plan_url: str
    source_page: int
    display_order: int


class CityViewInventory(BaseModel):
    units: list[CityViewUnit]
    total: int
    counts: dict[str, int]


class CityViewStatusUpdate(BaseModel):
    status: CityViewStatus
