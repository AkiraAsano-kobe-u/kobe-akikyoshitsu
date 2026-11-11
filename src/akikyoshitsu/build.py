"""全 source を解析して data/<学期>/occupancy.json と report.json を作る."""
from __future__ import annotations

import collections
import datetime
import json
from pathlib import Path

from . import parsers, sources
from .core import DAYS, resolve_rooms


def slot(day: str, quarter: str, period: int) -> str:
    return f"{day}|{quarter}|{period}"


def build(term: str, refresh: bool = False, root: Path = sources.ROOT) -> dict:
    meta, entries = sources.load_term(term, root)
    occupancy: dict[str, dict[str, set[str]]] = collections.defaultdict(lambda: collections.defaultdict(set))
    used_by: dict[str, set[str]] = collections.defaultdict(set)
    source_info, ignored = [], {}
    for source in entries:
        path = sources.fetch(source, term, refresh, root)
        records = parsers.parse(path, source)
        dropped: collections.Counter[str] = collections.Counter()
        kept = 0
        for record in records:
            rooms = resolve_rooms(record.token, source)
            if not rooms:
                dropped[record.token] += 1
            for area, room in rooms:
                key = slot(record.day, record.quarter, record.period)
                occupancy[area][room].add(key)
                used_by[f"{area}|{room}|{key}"].add(source["id"])
                kept += 1
        source_info.append({
            "id": source["id"], "title": source["title"], "url": source["url"],
            "page": source.get("page", ""), "sha256": sources.sha256(path), "slots": kept,
        })
        ignored[source["id"]] = dict(sorted(dropped.items(), key=lambda kv: -kv[1]))

    order = {d: i for i, d in enumerate(DAYS)}

    def slot_key(s: str):
        day, quarter, period = s.split("|")
        return (quarter, order[day], int(period))

    data = {
        "term": meta["id"], "title": meta["title"], "quarters": meta["quarters"],
        "generated": datetime.date.today().isoformat(),
        "sources": source_info,
        "areas": {a: {r: sorted(s, key=slot_key) for r, s in sorted(rooms.items())} for a, rooms in sorted(occupancy.items())},
    }
    report = {"ignored_tokens": ignored, "used_by": {k: sorted(v) for k, v in sorted(used_by.items())}}
    out = root / "data" / term
    out.mkdir(parents=True, exist_ok=True)
    (out / "occupancy.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return data
