from __future__ import annotations

from typing import TypedDict


class CityViewUnitSeed(TypedDict):
    unit_code: str
    tower: str
    floor_number: int | None
    floor_label: str
    bedrooms: int
    residence_type: str
    view: str
    suite_area_sqm: int
    balcony_area_sqm: int
    total_area_sqm: int
    floor_plan_url: str
    source_page: int
    display_order: int


def _plan(tower: str, bedrooms: int, view_key: str) -> str:
    tower_key = tower.lower().replace(" ", "-")
    return f"/ona-assets/cityview/floorplans/{tower_key}-{bedrooms}-{view_key}.jpg"


def _unit(
    *,
    tower: str,
    floor: int,
    suffix: int,
    bedrooms: int,
    view: str,
    suite: int,
    balcony: int,
    total: int,
    plan_view_key: str,
    source_page: int,
) -> CityViewUnitSeed:
    tower_letter = tower[-1]
    return {
        "unit_code": f"{tower_letter}-{floor}{suffix:02d}",
        "tower": tower,
        "floor_number": floor,
        "floor_label": f"{floor:02d}",
        "bedrooms": bedrooms,
        "residence_type": f"{bedrooms} Bedroom",
        "view": view,
        "suite_area_sqm": suite,
        "balcony_area_sqm": balcony,
        "total_area_sqm": total,
        "floor_plan_url": _plan(tower, bedrooms, plan_view_key),
        "source_page": source_page,
        "display_order": floor * 10 + suffix,
    }


def _penthouse(
    *,
    tower: str,
    penthouse_number: int,
    bedrooms: int,
    suite: int,
    balcony: int,
    total: int,
    source_page: int,
) -> CityViewUnitSeed:
    tower_letter = tower[-1]
    return {
        "unit_code": f"{tower_letter}-P{penthouse_number}",
        "tower": tower,
        "floor_number": None,
        "floor_label": "Penthouse",
        "bedrooms": bedrooms,
        "residence_type": f"{bedrooms} Bedroom Penthouse",
        "view": "Supreme Ocean & Sunrise Views",
        "suite_area_sqm": suite,
        "balcony_area_sqm": balcony,
        "total_area_sqm": total,
        "floor_plan_url": f"/ona-assets/cityview/floorplans/{tower.lower().replace(' ', '-')}-penthouse-{bedrooms}.jpg",
        "source_page": source_page,
        "display_order": 1000 + penthouse_number,
    }


def build_cityview_units() -> list[CityViewUnitSeed]:
    units: list[CityViewUnitSeed] = []

    # Tower A - levels 1 to 3 (West / East types)
    for floor in range(1, 4):
        units.extend(
            [
                _unit(tower="Tower A", floor=floor, suffix=1, bedrooms=3, view="West", suite=169, balcony=67, total=236, plan_view_key="west", source_page=5),
                _unit(tower="Tower A", floor=floor, suffix=2, bedrooms=2, view="West", suite=146, balcony=56, total=202, plan_view_key="west", source_page=3),
                _unit(tower="Tower A", floor=floor, suffix=3, bedrooms=2, view="East", suite=146, balcony=60, total=206, plan_view_key="east", source_page=4),
                _unit(tower="Tower A", floor=floor, suffix=4, bedrooms=3, view="East", suite=173, balcony=67, total=240, plan_view_key="east", source_page=6),
            ]
        )

    # Tower A - levels 4 to 11 (Ocean / Sunrise types)
    for floor in range(4, 12):
        units.extend(
            [
                _unit(tower="Tower A", floor=floor, suffix=1, bedrooms=3, view="Ocean View", suite=169, balcony=67, total=236, plan_view_key="ocean", source_page=9),
                _unit(tower="Tower A", floor=floor, suffix=2, bedrooms=2, view="Ocean View", suite=146, balcony=56, total=202, plan_view_key="ocean", source_page=7),
                _unit(tower="Tower A", floor=floor, suffix=3, bedrooms=2, view="Sunrise View", suite=146, balcony=60, total=206, plan_view_key="sunrise", source_page=8),
                _unit(tower="Tower A", floor=floor, suffix=4, bedrooms=3, view="Sunrise View", suite=167, balcony=73, total=240, plan_view_key="sunrise", source_page=10),
            ]
        )

    units.extend(
        [
            _penthouse(tower="Tower A", penthouse_number=1, bedrooms=3, suite=303, balcony=116, total=419, source_page=11),
            _penthouse(tower="Tower A", penthouse_number=2, bedrooms=4, suite=347, balcony=140, total=487, source_page=12),
        ]
    )

    # Tower B - levels 1 to 3 (West / East types)
    for floor in range(1, 4):
        units.extend(
            [
                _unit(tower="Tower B", floor=floor, suffix=1, bedrooms=3, view="West", suite=173, balcony=67, total=240, plan_view_key="west", source_page=16),
                _unit(tower="Tower B", floor=floor, suffix=2, bedrooms=2, view="West", suite=146, balcony=60, total=206, plan_view_key="west", source_page=14),
                _unit(tower="Tower B", floor=floor, suffix=3, bedrooms=2, view="East", suite=146, balcony=60, total=206, plan_view_key="east", source_page=15),
                _unit(tower="Tower B", floor=floor, suffix=4, bedrooms=3, view="East", suite=170, balcony=70, total=240, plan_view_key="east", source_page=17),
            ]
        )

    # Tower B - levels 4 and 5 retain East-facing 03/04 homes.
    for floor in range(4, 6):
        units.extend(
            [
                _unit(tower="Tower B", floor=floor, suffix=1, bedrooms=3, view="Ocean View", suite=173, balcony=67, total=240, plan_view_key="ocean", source_page=20),
                _unit(tower="Tower B", floor=floor, suffix=2, bedrooms=2, view="Ocean View", suite=146, balcony=60, total=206, plan_view_key="ocean", source_page=18),
                _unit(tower="Tower B", floor=floor, suffix=3, bedrooms=2, view="East", suite=146, balcony=60, total=206, plan_view_key="east", source_page=15),
                _unit(tower="Tower B", floor=floor, suffix=4, bedrooms=3, view="East", suite=170, balcony=70, total=240, plan_view_key="east", source_page=17),
            ]
        )

    # Tower B - levels 6 to 11 (Ocean / Sunrise types)
    for floor in range(6, 12):
        units.extend(
            [
                _unit(tower="Tower B", floor=floor, suffix=1, bedrooms=3, view="Ocean View", suite=173, balcony=67, total=240, plan_view_key="ocean", source_page=20),
                _unit(tower="Tower B", floor=floor, suffix=2, bedrooms=2, view="Ocean View", suite=146, balcony=60, total=206, plan_view_key="ocean", source_page=18),
                _unit(tower="Tower B", floor=floor, suffix=3, bedrooms=2, view="Sunrise View", suite=146, balcony=60, total=206, plan_view_key="sunrise", source_page=19),
                _unit(tower="Tower B", floor=floor, suffix=4, bedrooms=3, view="Sunrise View", suite=173, balcony=67, total=240, plan_view_key="sunrise", source_page=21),
            ]
        )

    units.extend(
        [
            _penthouse(tower="Tower B", penthouse_number=1, bedrooms=3, suite=303, balcony=120, total=423, source_page=22),
            _penthouse(tower="Tower B", penthouse_number=2, bedrooms=4, suite=357, balcony=134, total=491, source_page=23),
        ]
    )

    return sorted(units, key=lambda item: (item["tower"], item["display_order"]))


CITYVIEW_UNITS = build_cityview_units()
