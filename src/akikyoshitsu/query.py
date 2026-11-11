"""occupancy.json への問い合わせ."""
from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

from .core import DAYS, PERIODS
from .sources import ROOT


def latest_term(root: Path = ROOT) -> str:
    terms = sorted(p.parent.name for p in (root / "data").glob("*/occupancy.json"))
    if not terms:
        raise FileNotFoundError("data/<学期>/occupancy.json がありません。先に `akikyoshitsu build` を実行してください")
    return terms[-1]


def load(term: str | None = None, root: Path = ROOT) -> dict:
    term = term or latest_term(root)
    return json.loads((root / "data" / term / "occupancy.json").read_text(encoding="utf-8"))


def quarter_on(data: dict, date: datetime.date) -> str | None:
    for quarter, (start, end) in data["quarters"].items():
        if datetime.date.fromisoformat(start) <= date <= datetime.date.fromisoformat(end):
            return quarter
    return None


def period_at(time: datetime.time) -> int | None:
    """その時刻に行われている、または次に始まる時限."""
    hhmm = time.hour * 100 + time.minute
    return next((p for p, (_, end) in PERIODS.items() if hhmm <= end), None)


def building(room: str) -> str:
    m = re.match(r"LR|[A-Z]\d?(?=-)|\d[EW](?=-)|[A-Z]+|[^\d]+", room)
    return m.group() if m else room


def free_rooms(data: dict, day: str, quarter: str, period: int) -> dict[str, list[tuple[str, int]]]:
    """エリアごとに (教室, 何限まで続けて空いているか) を返す."""
    if day not in DAYS:
        raise ValueError(f"曜日が不正です: {day}")
    last = max(PERIODS)
    out: dict[str, list[tuple[str, int]]] = {}
    for area, rooms in data["areas"].items():
        for room, slots in rooms.items():
            busy = {int(s.rsplit("|", 1)[1]) for s in slots if s.startswith(f"{day}|{quarter}|")}
            if period in busy:
                continue
            until = period
            while until < last and until + 1 not in busy:
                until += 1
            out.setdefault(area, []).append((room, until))
    return out
