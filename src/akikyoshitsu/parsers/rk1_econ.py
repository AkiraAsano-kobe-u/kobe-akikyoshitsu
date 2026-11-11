"""経済学部・経済学研究科の後期時間割: 行=曜日(・学年)、列=1〜5時限、各時限の右端が「教室」.

クォーターの欄は無い。科目名に【3Q】【4Q】と書かれたものだけそのクォーター、
それ以外は 3Q と 4Q の両方に入れる (【隔週】は毎週かどうか分からないので両方)。
表の下の「集中講義」の枠は日時が別に書かれているので読まない。
"""
from __future__ import annotations

import re
from pathlib import Path

from ..core import Record
from . import _pdf, _rokkodai1 as rk

TOL = 25.0  # 教室列は見出しの中心から左右この範囲


def parse(path: Path, source: dict) -> list[Record]:
    out: list[Record] = []
    for index, page in _pdf.pages(path):
        ws = _pdf.words(page)
        hs, _ = _pdf.segments(page)
        heads = rk.top_row(rk.room_header_words(ws))
        if len(heads) != 5:
            continue
        cols = [(h[0] + h[2]) / 2 for h in heads]
        labels = rk.label_chars(page, heads[0][0] - 100)
        if not labels:
            continue
        out += rk.grid_records(index, page, ws, hs, heads, tol=TOL, block=290.0, label_gap=100.0)
        out += _saturday(index, ws, cols, heads)
    return out


def _saturday(index, ws, cols, heads) -> list[Record]:
    """表の外に「（土3・4）演習・特殊研究」のように曜日時限を書いた行があれば、その教室を土曜に入れる."""
    out: list[Record] = []
    for label in ws:
        m = re.search(r"[（(]土([0-9・,、]+)[）)]", rk.nfkc(label[4]))
        if not m or label[1] < heads[0][3]:
            continue
        periods = [int(c) for c in re.findall(r"\d", m.group(1))]
        for w in ws:
            cx, cy = rk.center(w)
            if abs(cy - rk.center(label)[1]) <= 4 and any(abs(cx - x) <= TOL for x in cols):
                for token in rk.expand_rooms(w[4]):
                    for q in ("3Q", "4Q"):
                        out += [Record("土", q, p, token, f"p{index + 1} 土") for p in periods]
    return out
