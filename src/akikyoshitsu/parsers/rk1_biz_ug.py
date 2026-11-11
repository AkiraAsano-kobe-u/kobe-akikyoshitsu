"""経営学部の後期時間割 (1年生用・2年生以上用): 行=曜日、その中が 3Q / 4Q / S(セメスター) の3帯、列=1〜5時限.

左端の「3Q」「4Q」「S」のラベルが入っている帯がその科目のクォーターで、S は 3Q と 4Q の両方。
ページの下にある小さな表 (遠隔授業・オンデマンド) は帯の外なので読まない。

帯の境目は表の横幅いっぱいの細い黒罫線だが、行ごとの余計な罫線も混じるので、
曜日の境目 (太い罫線) の間で「各ラベルが自分の帯の縦の中央に来る」ように罫線の組を選ぶ。
"""
from __future__ import annotations

import itertools
from pathlib import Path

from ..core import Record
from . import _pdf, _rokkodai1 as rk

TOL = 11.0  # 教室列は見出しの中心から左右この範囲 (教員列は約24pt左)
QUARTERS = {"3Q": ("3Q",), "4Q": ("4Q",), "S": ("3Q", "4Q")}


def _rules(page) -> list[tuple[float, bool]]:
    """表の横幅の7割以上にわたる細い黒罫線 (y, 太いか) のリスト.

    罫線は列ごとに分割して描かれていることがあり、行ごとの塗りつぶし矩形も横に長いので、
    高さ1.5pt未満の線だけを集め、同じ y (±1.5pt) のものの長さを合計して判定する。
    """
    segs = []  # (y, x0, x1, 太さ)
    for d in page.get_drawings():
        for item in d["items"]:
            if item[0] == "re" and item[1].width > 20 and item[1].height < 1.5:
                segs.append((item[1].y0, item[1].x0, item[1].x1, item[1].height))
            elif item[0] == "l" and abs(item[1].y - item[2].y) < 0.7 and abs(item[1].x - item[2].x) > 20:
                segs.append((item[1].y, min(item[1].x, item[2].x), max(item[1].x, item[2].x), d.get("width") or 0.4))
    if not segs:
        return []
    width = max(x1 - x0 for _, x0, x1, _ in segs)
    segs.sort()
    groups: list[list[tuple]] = []
    for seg in segs:
        if groups and seg[0] - groups[-1][0][0] <= 1.5:
            groups[-1].append(seg)
        else:
            groups.append([seg])
    out: list[tuple[float, bool]] = []
    for group in groups:
        covered, end = 0.0, -1e9
        for _, x0, x1, _ in sorted(group, key=lambda g: g[1]):
            covered += max(0.0, x1 - max(x0, end))
            end = max(end, x1)
        if covered >= 0.7 * width:
            out.append((group[0][0], max(g[3] for g in group) >= 0.6))
    return out


def _split(top: float, bottom: float, inner: list[float], centers: list[float]) -> list[float] | None:
    """top〜bottom を len(centers) 個の帯に分ける罫線の組。各帯の中央が対応するラベルの中心に最も近い組."""
    n = len(centers)
    if n <= 1:
        return []
    best, best_cost = None, 1e18
    for combo in itertools.combinations(inner, n - 1):
        edges = [top, *combo, bottom]
        cost = sum(((edges[i] + edges[i + 1]) / 2 - c) ** 2 for i, c in enumerate(centers))
        if cost < best_cost:
            best, best_cost = list(combo), cost
    return best


def parse(path: Path, source: dict) -> list[Record]:
    out: list[Record] = []
    for index, page in _pdf.pages(path):
        ws = _pdf.words(page)
        heads = rk.top_row(rk.room_header_words(ws))
        if len(heads) != 5:
            continue
        cols = [(h[0] + h[2]) / 2 for h in heads]
        rules = [(y, thick) for y, thick in _rules(page) if y > heads[0][1] + 2]
        if not rules:
            continue
        days = rk.label_chars(page, 60)
        subs = sorted(
            (rk.center(w)[1], rk.nfkc(w[4]))
            for w in ws
            if rk.nfkc(w[4]) in QUARTERS and w[2] < 60 and w[1] > heads[0][3]
        )
        # 曜日の境目: 見出し直下の最初の罫線と、それより下の太い罫線
        edges = [rules[0][0]] + [y for y, thick in rules[1:] if thick and y > rules[0][0] + 5]
        intervals = list(zip(edges, edges[1:]))
        # 曜日ラベルが入っている区間だけが時間割の本体 (その下の小さな表や注記は含めない)
        body = [iv for iv in intervals if any(iv[0] <= (d[1] + d[3]) / 2 < iv[1] for d in days)]
        if len(body) != len(days):
            raise ValueError(f"biz p{index + 1}: 曜日ラベル {[d[4] for d in days]} と区間 {len(body)} 個が合わない")
        for day, (top, bottom) in zip(days, body):
            labels = [(c, t) for c, t in subs if top <= c < bottom]
            inner = [y for y, _ in rules if top + 3 < y < bottom - 3]
            cuts = _split(top, bottom, inner, [c for c, _ in labels])
            if cuts is None:
                raise ValueError(f"biz p{index + 1}: {day[4]} の帯を分けられない")
            bounds = [top, *cuts, bottom]
            for (y0, y1), (_, label) in zip(zip(bounds, bounds[1:]), labels):
                for w in ws:
                    cx, cy = rk.center(w)
                    if not y0 <= cy < y1:
                        continue
                    col = next((c for c, x in enumerate(cols) if abs(cx - x) <= TOL), None)
                    if col is None:
                        continue
                    for token in rk.expand_rooms(w[4]):
                        for q in QUARTERS[label]:
                            out.append(Record(day[4], q, col + 1, token, f"p{index + 1} {label}"))
    return out
