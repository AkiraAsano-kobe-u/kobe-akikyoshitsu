"""格子型時間割の拡張版 (国際人間科学部 発達コミュニティ・環境共生・子ども教育 / 人間発達環境学研究科 / 国際文化学研究科).

`grid` パーサは 曜日ラベルの罫線が欠けていたり、教室列の見出しが隣の文字とくっついていたりする
表で取りこぼす。このモジュールは `grid` と同じ「教室列 × 曜日の帯」の考え方で、次を足したもの。

  - 曜日の帯 (source["day_bands"]):
      "band" (既定) 曜日ラベルを挟む水平罫線 (grid._band)。ラベル列の罫線が欠けていると帯が潰れる
      "rule"        曜日ラベルのすぐ右にある縦罫線の区切り (曜日ごとに途切れる列境界線)
      "full"        教室列をまたぐ全幅の水平罫線 (分割された線分も合算) のうち、ラベルを挟む最も近い2本
  - クォーターは 1) ページ上部の「第3クォーター」「(第3Q)」 2) 無ければ source["quarters"] の両方。
    「後期」通しの科目は両クォーターに入れる (迷ったら使用中に倒す)。
  - 教室列の求め方 (source["columns"]):
      "rules"  (既定) 「教室」見出しを挟む縦罫線から求める
      "window" 見出し語 (「教室」「教室時間割」「教室開講」など先頭が「教室」の語) の左端から固定幅
  - source["after"]  : その文字を含む語より下だけを対象にする (1ページに前期表と後期表が並ぶ PDF 用)
  - source["star_prefix"] : 「★B202」の ★ をこの接頭辞に置き換える。core.split_token は ★ を捨ててしまうので、
                            ★ の意味 (鶴甲第二キャンパスの教室) を「鶴2B202」という表記にして resolve_rooms まで運ぶ。
  - 紙面に見えない文字 (白で描かれた消し忘れ) は捨てる (_ink)。source["hidden_text"] = true なら捨てない。
  - source["sixth_marker"] = true : 5限の列に「【6時限】」の見出しがあるとき、その下の行 (同じ曜日の帯) は6限として扱う
  - source["extra"]  : [{day, quarters, periods, token, note}] PDF の後に出た時間割変更などで、PDFの表に無い使用中コマを足す
  - source["period_map"] : {"5": [5, 6], "7": []} 列番号 → 標準時限の対応 (大学院は5限が 17:50-19:20 など時刻が違う)
"""
from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from pathlib import Path

from ..core import DAYS, PERIODS, Record
from . import _pdf
from ._ink import Ink
from ._words import words as _words
from .grid import _band, _page_quarter, _room_columns


def _norm(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def _quarter_of(text: str) -> str | None:
    """「第3クォーター」「(第3Q)」から 3Q を取り出す."""
    t = _norm(text)
    m = re.search(r"第\s*([1-4])\s*(?:クォーター|Q)", t)
    return f"{m.group(1)}Q" if m else _page_quarter(text)


def _window_columns(ws, width: float = 42.0, left: float = 8.0):
    heads = [w for w in ws if _norm(w[4]).startswith("教室")]
    if not heads:
        return [], None
    top = min(h[1] for h in heads)
    heads = sorted((h for h in heads if abs(h[1] - top) < 12), key=lambda h: h[0])
    return [(h[0] - left, h[0] + width - left) for h in heads], top


def _full_rules(hs, x_lo: float, x_hi: float, coverage: float = 0.9) -> list[float]:
    """x_lo..x_hi の 90% 以上を覆う水平罫線の y (線分は y が近いものを合算する)."""
    groups: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for y, a, b in hs:
        groups[round(y / 1.5)].append((max(a, x_lo), min(b, x_hi)))
    ys = []
    for key, segs in groups.items():
        segs = sorted(s for s in segs if s[1] > s[0])
        covered, end = 0.0, x_lo
        for a, b in segs:
            a = max(a, end)
            if b > a:
                covered += b - a
                end = b
        if covered >= coverage * (x_hi - x_lo):
            ys.append(key * 1.5)
    return sorted(ys)


def parse(path: Path, source: dict) -> list[Record]:
    wanted = set(source.get("quarters", ("3Q", "4Q")))
    default_q = [q for q in ("3Q", "4Q") if q in wanted] or sorted(wanted)
    pmap = {int(k): v for k, v in source.get("period_map", {}).items()}
    star = source.get("star_prefix")
    after = _norm(source["after"]) if source.get("after") else None
    out: list[Record] = []
    for index, page in _pdf.pages(path):
        ws = _words(page)
        hs, vs = _pdf.segments(page)
        y0 = 0.0
        if after:
            marks = [w[1] for w in ws if after in _norm(w[4])]
            if not marks:
                continue
            y0 = min(marks) - 1
            ws = [w for w in ws if w[1] >= y0]
            hs = [h for h in hs if h[0] >= y0]
        cols, head_y = (_window_columns(ws) if source.get("columns") == "window" else _room_columns(ws, vs))
        if not cols:
            continue
        x_lo, x_hi = min(c[0] for c in cols), max(c[1] for c in cols)
        rules = [y for y in _full_rules(hs, x_lo, x_hi) if y > head_y]
        label_x = x_lo - 60
        page_q = _quarter_of(" ".join(w[4] for w in ws if y0 <= w[1] < head_y))
        quarters = [page_q] if page_q else default_q

        mode = source.get("day_bands", "band")
        bands = []  # (y上, y下, 曜日)
        for d in (w for w in ws if w[4] in DAYS and w[0] < label_x and w[1] > head_y):
            cy = (d[1] + d[3]) / 2
            if mode == "band":
                top, bottom = _band(hs, (d[0] + d[2]) / 2, cy)
            elif mode == "rule":
                near = [v for v in vs if d[2] - 1 <= v[0] <= d[2] + 30 and v[1] <= cy <= v[2] and v[2] - v[1] > 60]
                best = min(near, key=lambda v: (v[0], v[2] - v[1])) if near else None
                top, bottom = (best[1], best[2]) if best else (None, None)
            else:
                up = [y for y in rules if y < cy - 1]
                down = [y for y in rules if y > cy + 1]
                top, bottom = (max(up) if up else None, min(down) if down else None)
            if top is not None and bottom is not None:
                bands.append((top, bottom, d[4]))

        ink = None if source.get("hidden_text") else Ink(page)
        hits = []  # (語, 列, 帯)
        for word in ws:
            cx, cy = (word[0] + word[2]) / 2, (word[1] + word[3]) / 2
            col = next((i + 1 for i, c in enumerate(cols) if c[0] <= cx <= c[1]), None)
            band = next((b for b in bands if b[0] <= cy <= b[1]), None)
            if col is None or band is None or cy <= head_y:
                continue
            if ink is not None and not ink.visible(word[:4]):
                continue
            hits.append((word, col, band))
        # 5限の列の中に「【6時限】」の見出しがあれば、その下の行 (同じ曜日の帯の中) は6限の授業
        sixth = [w for w in ws if _norm(w[4]).strip("【】") == "6時限"] if source.get("sixth_marker") else []
        shifted = []
        for word, col, band in hits:
            if col == len(cols) and any(m[1] < word[1] and band[0] <= m[1] <= band[1] and m[0] >= cols[-1][0] - 400 for m in sixth):
                shifted.append((word, col + 1, band))
            else:
                shifted.append((word, col, band))
        hits = shifted
        # 「B304」の下の行に「-306」と折り返された範囲表記を「B304-306」に戻す
        merged: dict[int, str] = {}
        for k, (word, col, band) in enumerate(hits):
            if re.fullmatch(r"-\d{3}", _norm(word[4])):
                above = [j for j, (w, c, b) in enumerate(hits) if c == col and b is band and abs(w[3] - word[1]) < 3 and abs(w[0] - word[0]) < 12]
                if above:
                    merged[above[0]] = hits[above[0]][0][4] + word[4]
                    merged[k] = ""
        for k, (word, col, band) in enumerate(hits):
            text = merged.get(k, word[4])
            if not text:
                continue
            token = text.replace("★", star) if star else text
            for period in pmap.get(col, [col]):
                if period not in PERIODS:
                    continue
                for quarter in quarters:
                    if quarter in wanted:
                        out.append(Record(band[2], quarter, period, token, f"p{index + 1}"))
    for e in source.get("extra", []):
        for quarter in e.get("quarters", default_q):
            for period in e["periods"]:
                if quarter in wanted:
                    out.append(Record(e["day"], quarter, period, e["token"], "extra: " + e.get("note", "")))
    return out
