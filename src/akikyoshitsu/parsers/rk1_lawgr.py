"""法学研究科(博士前期・後期)と法科大学院の時間割: 行=曜日、列=時限、各時限の右端に「教室」列.

後期(3Q・4Q)通しの表で、クォーター別の欄は無い -> 常に 3Q と 4Q の両方に入れる。
(法学基礎論特殊講義 ※7 のように第3Qだけの科目もあるが、表からは読み取れないので使用中に倒す)

source["columns"] は「教室」列ごとの時限リスト (左から順)。例:
  [[1],[2],[3],[4],[5,6],[]]
法学研究科の「(夜)1時限 17:50-19:20」は標準の5限(17:00-18:30)と6限(18:50-20:20)の両方に
重なるので [5,6] とする。「(夜)2時限 19:30-21:00」はどの時限にも当たらないので [] (捨てる)。
"""
from __future__ import annotations

from pathlib import Path

from ..core import Record
from . import _pdf, _rokkodai1 as rk


def parse(path: Path, source: dict) -> list[Record]:
    columns = source["columns"]
    quarters = source.get("quarters", ("3Q", "4Q"))
    out: list[Record] = []
    for index, page in _pdf.pages(path):
        ws = _pdf.words(page)
        hs, _ = _pdf.segments(page)
        heads = rk.room_header_words(ws)
        first = rk.top_row(heads)
        if len(first) != len(columns):
            continue
        top = first[0][1]
        lower = [h[1] for h in heads if h[1] > top + 100]  # 集中講義など下の表の見出し
        bottom = min(lower) - 5 if lower else page.rect.y1
        bands = rk.day_bands(page, hs, label_max_x=first[0][0] - 60, bottom=bottom)
        for w in ws:
            cx, cy = rk.center(w)
            if cy < top:
                continue
            col = next((i for i, h in enumerate(first) if abs(cx - (h[0] + h[2]) / 2) <= 14), None)
            band = next((b for b in bands if b.has(cy)), None)
            if col is None or band is None:
                continue
            for token in rk.expand_rooms(w[4]):
                for period in columns[col]:
                    for q in quarters:
                        out.append(Record(band.label, q, period, token, f"p{index + 1}"))
    return out
