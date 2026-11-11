"""格子型の時間割表 (行=曜日×クォーター、列=時限、各時限ブロックの右端に「教室」列).

工学部各学科・システム情報学部・工学研究科・国際人間科学部グローバル文化学科などの書式。
教室列と行の範囲は罫線から求め、その中に入った単語を教室表記として拾う。

行のクォーターは次の順で決める:
  1. 左端に "3Q"/"4Q" のラベルがある -> その帯
  2. ページ上部に「第3クォーター」等がある -> ページ全体がそのクォーター (行=曜日)
  3. 左端に "前期"/"後期" のラベルがある -> 後期は 3Q と 4Q の両方、前期は 1Q と 2Q の両方
対象学期に含まれないクォーターの行は source["quarters"] で落とす。
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from ..core import DAYS, Record
from . import _pdf

HEAD = ("教室", "教\u3000室")
SEMESTER = {"前期": ("1Q", "2Q"), "後期": ("3Q", "4Q")}


def _band(hs, cx, cy):
    """点 (cx, cy) を上下から挟む、その x を通る水平罫線の y."""
    ys = [y for y, x0, x1 in hs if x0 - 1 <= cx <= x1 + 1]
    up = [y for y in ys if y < cy - 1]
    down = [y for y in ys if y > cy + 1]
    return (max(up) if up else None, min(down) if down else None)


def _room_columns(ws, vs):
    heads = [w for w in ws if w[4] in HEAD]
    for k in (w for w in ws if w[4] == "教"):  # 「教 室」と離して書かれた見出し
        for s in (w for w in ws if w[4] == "室"):
            if abs(s[1] - k[1]) < 2 and 0 < s[0] - k[2] < 12:
                heads.append((k[0], k[1], s[2], s[3], "教室"))
    if not heads:
        return [], None
    top = min(h[1] for h in heads)
    heads = sorted((h for h in heads if abs(h[1] - top) < 3), key=lambda h: h[0])
    cols = []
    for h in heads:
        cy = (h[1] + h[3]) / 2
        xs = [x for x, a, b in vs if a - 2 <= cy <= b + 2]
        left = [x for x in xs if x < h[0] + 1]
        right = [x for x in xs if x > h[2] - 1]
        if left and right:
            cols.append((max(left), min(right)))
    return cols, top


def _page_quarter(text: str) -> str | None:
    m = re.search(r"第\s*([1-4])\s*クォーター", unicodedata.normalize("NFKC", text))
    return f"{m.group(1)}Q" if m else None


def parse(path: Path, source: dict) -> list[Record]:
    wanted = set(source.get("quarters", ("3Q", "4Q")))
    out: list[Record] = []
    for index, page in _pdf.pages(path):
        ws = _pdf.words(page)
        hs, vs = _pdf.segments(page)
        cols, head_y = _room_columns(ws, vs)
        if not cols:
            continue
        label_x = min(c[0] for c in cols) - 60  # 曜日・クォーターのラベルは表の左端にある
        day_bands = []
        for d in (w for w in ws if w[4] in DAYS and w[0] < label_x):
            b = _band(hs, (d[0] + d[2]) / 2, (d[1] + d[3]) / 2)
            if None not in b:
                day_bands.append((b, d[4]))

        labels = []
        for q in (w for w in ws if w[0] < label_x):
            text = unicodedata.normalize("NFKC", q[4])
            if re.fullmatch(r"[1-4]Q", text) or text in SEMESTER:
                labels.append((q, text))
        page_q = _page_quarter(" ".join(w[4] for w in ws if w[1] < head_y))
        if any(text not in SEMESTER for _, text in labels):
            labels = [(q, text) for q, text in labels if text not in SEMESTER]
        elif page_q:
            labels = []

        bands = []  # (y範囲, [クォーター], 曜日)
        for q, text in labels:
            cx, cy = (q[0] + q[2]) / 2, (q[1] + q[3]) / 2
            b = _band(hs, cx, cy)
            day = next((d for bb, d in day_bands if bb[0] - 1 <= cy <= bb[1] + 1), None)
            if None in b or day is None:
                continue
            bands.append((b, SEMESTER.get(text, (text,)), day))
        if not bands and page_q:
            bands = [(b, (page_q,), d) for b, d in day_bands]

        for word in ws:
            cx, cy = (word[0] + word[2]) / 2, (word[1] + word[3]) / 2
            period = next((i + 1 for i, c in enumerate(cols) if c[0] <= cx <= c[1]), None)
            band = next((b for b in bands if b[0][0] <= cy <= b[0][1]), None)
            if period is None or band is None:
                continue
            for quarter in band[1]:
                if quarter in wanted:
                    out.append(Record(band[2], quarter, period, word[4], f"p{index + 1}"))
    return out
