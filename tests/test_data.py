"""コミット済みの data/ に対する検査。PDFが無い環境 (CI) でも走る."""
import json
import re

import pytest

from akikyoshitsu import sources
from akikyoshitsu.core import DAYS, PERIODS

TERMS = sorted(p.parent.name for p in (sources.ROOT / "data").glob("*/occupancy.json"))


@pytest.fixture(params=TERMS)
def term(request):
    directory = sources.ROOT / "data" / request.param
    data = json.loads((directory / "occupancy.json").read_text(encoding="utf-8"))
    report = json.loads((directory / "report.json").read_text(encoding="utf-8"))
    return request.param, data, report


def test_data_exists():
    assert TERMS


def test_every_source_is_built_and_not_empty(term):
    name, data, _ = term
    _, entries = sources.load_term(name)
    built = {s["id"]: s for s in data["sources"]}
    assert set(built) == {s["id"] for s in entries}, "sources/ を変えたら build し直す"
    for source in entries:
        assert built[source["id"]]["slots"] >= source.get("min_slots", 1), source["id"]


def test_slots_are_well_formed(term):
    _, data, _ = term
    assert data["areas"]
    for area, rooms in data["areas"].items():
        assert rooms, area
        for room, slots in rooms.items():
            assert slots, (area, room)
            for slot in slots:
                day, quarter, period = slot.split("|")
                assert day in DAYS and quarter in data["quarters"] and int(period) in PERIODS, (area, room, slot)


def test_report_matches_occupancy(term):
    _, data, report = term
    listed = {f"{a}|{r}|{s}" for a, rooms in data["areas"].items() for r, slots in rooms.items() for s in slots}
    assert listed == set(report["used_by"])


def test_no_room_name_spans_two_spellings(term):
    """同じエリアに「B210」と「Ｂ２１０」のような表記ゆれが残っていない."""
    _, data, _ = term
    for area, rooms in data["areas"].items():
        keys = [re.sub(r"[\s\-‐－ー]", "", r).upper() for r in rooms]
        assert len(keys) == len(set(keys)), area
