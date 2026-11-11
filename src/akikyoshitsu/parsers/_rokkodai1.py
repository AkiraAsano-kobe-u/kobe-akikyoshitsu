"""六甲台第1キャンパス(法・経済・経営・国際協力)の時間割パーサ共通部品.

各学部の時間割は書式がばらばらなので、パーサは学部ごとに分けるが、
「教室」見出しの位置から列を決める・曜日ラベルから行の帯を決める・
科目名から開講クォーターを読む、といった処理はここで共有する。
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from ..core import DAYS
from . import _pdf


def nfkc(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


@dataclass(frozen=True)
class Band:
    """曜日などの縦方向の帯 [y0, y1)."""

    label: str
    y0: float
    y1: float

    def has(self, cy: float) -> bool:
        return self.y0 <= cy < self.y1


def center(w) -> tuple[float, float]:
    return (w[0] + w[2]) / 2, (w[1] + w[3]) / 2


def room_header_words(ws) -> list:
    """「教室」見出し (「教 室」と離れたものも含む)."""
    heads = [w for w in ws if nfkc(w[4]) in ("教室", "教\u3000室", "Room")]
    for k in (w for w in ws if w[4] == "教"):
        for s in (w for w in ws if w[4] == "室"):
            if abs(s[1] - k[1]) < 2 and 0 < s[0] - k[2] < 12:
                heads.append((k[0], k[1], s[2], s[3], "教室"))
    return heads


def top_row(heads, tolerance: float = 3.0) -> list:
    """最上段にある見出しだけを左から順に返す."""
    if not heads:
        return []
    top = min(h[1] for h in heads)
    return sorted((h for h in heads if abs(h[1] - top) < tolerance), key=lambda h: h[0])


def label_chars(page, max_x: float, day_chars: str = DAYS) -> list[tuple]:
    """左端の曜日ラベル (x0, y0, x1, y1, 文字).

    科目名と接して「木法学文献研究」のように1語に融合することがあるので、文字単位で拾う。
    最も左のものと同じ x にあるものだけを採る (科目名の中の「金」「木」を除く)。
    """
    chars = []
    for block in page.get_text("rawdict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                for c in span["chars"]:
                    t = nfkc(c["c"])
                    if len(t) == 1 and t in day_chars and c["bbox"][2] < max_x:
                        chars.append((*c["bbox"], t))
    if not chars:
        return []
    x = min(c[0] for c in chars)
    return sorted((c for c in chars if abs(c[0] - x) < 1.5), key=lambda c: c[1])


def day_bands(page, hs, label_max_x: float, bottom: float | None = None, day_chars: str = DAYS) -> list[Band]:
    """左端の曜日ラベルと、そのラベルの枠を区切る水平罫線から、曜日ごとの帯を作る.

    表の内側の行罫線はラベル列を通らないので、ラベルの x を横切る罫線だけを使う。
    """
    starts = []
    for x0, y0, x1, y1, day in label_chars(page, label_max_x, day_chars):
        cx = (x0 + x1) / 2
        ys = [y for y, a, b in hs if a <= cx <= b and b - a > 20 and y <= y0 + 2]
        starts.append((max(ys) if ys else y0 - 2, day))
    if bottom is None and starts:
        # 最後の曜日の下端: その曜日のラベルの枠を区切る、次の水平罫線 (無ければページの下端)
        x0, y0, x1, y1, _ = label_chars(page, label_max_x, day_chars)[-1]
        cx = (x0 + x1) / 2
        below = [y for y, a, b in hs if a <= cx <= b and b - a > 20 and y > starts[-1][0] + 5]
        bottom = min(below) if below else page.rect.y1
    bands = []
    for i, (y0, day) in enumerate(starts):
        y1 = starts[i + 1][0] if i + 1 < len(starts) else bottom
        bands.append(Band(day, y0, y1))
    return bands


def expand_rooms(text: str) -> list[str]:
    """「Ⅱ104・106」のように建物記号を省略した並記を「Ⅱ104」「Ⅱ106」に展開する.

    (core.split_token は「・」で分割するので、そのままだと「106」が建物不明になる)
    """
    t = nfkc(text)
    m = re.fullmatch(r"([A-Zア-ン]+)(\d{3})[・,、/](\d{3})", t)
    if m:
        return [f"{m.group(1)}{m.group(2)}", f"{m.group(1)}{m.group(3)}"]
    return [text]


# 科目名に書かれた開講クォーターの注記
_Q_ONLY = re.compile(r"[【\[（(]\s*([34])\s*Q\s*(?:のみ(?:開講)?)?\s*[】\]）)]")
_Q_ONLY2 = re.compile(r"([34])\s*Q\s*のみ")
_Q_ONLY3 = re.compile(r"\(\s*([34])(?:rd|th)\s*Q\s*\)", re.I)  # (4th Q)


def quarters_from_text(text: str, default: tuple[str, ...] = ("3Q", "4Q")) -> tuple[str, ...]:
    """科目名の【3Q】【4Qのみ開講】などから開講クォーターを読む。両方書かれていれば/無ければ default."""
    t = nfkc(text)
    found = {f"{m.group(1)}Q" for rx in (_Q_ONLY, _Q_ONLY2, _Q_ONLY3) for m in rx.finditer(t)}
    if len(found) == 1:
        return tuple(sorted(found))
    return default


def words_in(ws, x0: float, x1: float, y0: float, y1: float) -> list:
    return [w for w in ws if x0 <= center(w)[0] < x1 and y0 <= center(w)[1] < y1]


def pages_of(path):
    yield from _pdf.pages(path)


def marked_quarters(room, block, room_words, reach: float = 14.0) -> tuple[str, ...]:
    """教室 room の科目に付いた【3Q】【4Qのみ開講】などの注記から開講クォーターを返す (無ければ両方).

    block は同じ時限の科目名・教員・コード欄の単語、room_words は同じ列の教室候補。
    注記の単語を、同じ行の教室候補、無ければ上下で最も近い教室候補に結び付け、
    それが room ならその注記を採る。科目名が2行に折り返して注記が教室と別の行にある場合に対応する。
    """
    cy = center(room)[1]
    found: set[str] = set()
    for v in block:
        q = quarters_from_text(v[4], default=())
        if not q:
            continue
        vy = center(v)[1]
        same = [r for r in room_words if abs(center(r)[1] - vy) <= 3.5]
        if same:
            owner = same
        else:
            near = sorted(((abs(center(r)[1] - vy), r) for r in room_words if abs(center(r)[1] - vy) <= reach), key=lambda t: t[0])
            # 最も近い教室候補の持ち物とする。同じ距離で2つ並ぶときは決められないので誰の物にもしない (=両クォーター)
            owner = [near[0][1]] if near and (len(near) == 1 or near[1][0] - near[0][0] > 1.5) else []
        if any(r is room for r in owner):
            found.add(q[0])
    return tuple(sorted(found)) if len(found) == 1 else ("3Q", "4Q")


def grid_records(index, page, ws, hs, heads, tol: float, block: float, label_gap: float = 60.0):
    """行=曜日、列=時限(各時限の右端が教室列) の表から Record を作る.

    heads: 最上段の「教室」見出し (時限の数だけ、左から順)。
    教室列は見出しの中心から左右 tol。科目名の注記 (【3Qのみ】) は教室列の左 block の範囲から探す。
    表の下端は、最後の曜日の帯より下にある最初の長い罫線。
    """
    from ..core import Record

    out: list[Record] = []
    cols = [(h[0] + h[2]) / 2 for h in heads]
    label_max_x = heads[0][0] - label_gap
    labels = label_chars(page, label_max_x)
    if not labels:
        return out
    bands = day_bands(page, hs, label_max_x=label_max_x)
    for band in bands:
        rooms = []  # (列, 単語)
        for w in ws:
            cx, cy = center(w)
            if not band.has(cy) or cy < heads[0][3]:
                continue
            col = next((i for i, x in enumerate(cols) if abs(cx - x) <= tol), None)
            if col is not None:
                rooms.append((col, w))
        for col, w in rooms:
            near = [v for v in ws if cols[col] - block < center(v)[0] < cols[col] - tol and band.has(center(v)[1])]
            quarters = marked_quarters(w, near, [r for c, r in rooms if c == col])
            for token in expand_rooms(w[4]):
                for q in quarters:
                    out.append(Record(band.label, q, col + 1, token, f"p{index + 1}"))
    return out
