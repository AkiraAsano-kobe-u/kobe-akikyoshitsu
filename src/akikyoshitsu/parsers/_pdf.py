"""PDF から「単語」と罫線を取り出す共通処理."""
from __future__ import annotations

from pathlib import Path

import pymupdf

Word = tuple[float, float, float, float, str]  # x0, y0, x1, y1, text
HSeg = tuple[float, float, float]  # y, x0, x1
VSeg = tuple[float, float, float]  # x, y0, y1


def pages(path: Path):
    """各ページを回転を解いた状態で返す."""
    doc = pymupdf.open(path)
    for index, page in enumerate(doc):
        page.remove_rotation()
        yield index, page


def words(page) -> list[Word]:
    return [(w[0], w[1], w[2], w[3], w[4]) for w in page.get_text("words")]


def segments(page) -> tuple[list[HSeg], list[VSeg]]:
    """ページ上の水平・垂直の罫線 (細い矩形や矩形の辺も含む)."""
    hs: list[HSeg] = []
    vs: list[VSeg] = []
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] == "l":
                a, b = item[1], item[2]
                if abs(a.y - b.y) < 0.7:
                    hs.append((a.y, min(a.x, b.x), max(a.x, b.x)))
                elif abs(a.x - b.x) < 0.7:
                    vs.append((a.x, min(a.y, b.y), max(a.y, b.y)))
            elif item[0] == "re":
                r = item[1]
                if r.height < 2.5:
                    hs.append((r.y0, r.x0, r.x1))
                elif r.width < 2.5:
                    vs.append((r.x0, r.y0, r.y1))
                else:
                    hs += [(r.y0, r.x0, r.x1), (r.y1, r.x0, r.x1)]
                    vs += [(r.x0, r.y0, r.y1), (r.x1, r.y0, r.y1)]
    return hs, vs


def lines(page, tolerance: float = 2.5) -> list[list[Word]]:
    """単語を行にまとめる (上から順、行内は左から順)."""
    ws = sorted(words(page), key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    out: list[list[Word]] = []
    for w in ws:
        cy = (w[1] + w[3]) / 2
        if out and abs((out[-1][0][1] + out[-1][0][3]) / 2 - cy) <= tolerance:
            out[-1].append(w)
        else:
            out.append([w])
    return [sorted(line, key=lambda w: w[0]) for line in out]
