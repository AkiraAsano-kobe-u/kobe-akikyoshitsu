"""文学部・人文学研究科の時間割表 (A0級の1枚物: 5曜日が横に並び、時限が縦に並ぶ).

書式の特徴 (grid との違い):
  * 曜日は横に5つの塊 (各塊に「授業形態」「教室」の見出し)。時限は左右端の「N時限」ラベル。
  * 時限の境目は、ページ幅のほぼ全長にわたる1本の水平罫線。
  * 教室は科目行ごとではなく結合セルに書かれ、複数科目で共有される。そのため
    「その塊・その時限の帯に入っている教室表記」をすべて使用中とみなす。
  * 「３・４限連続」「隔週 ４・５限連続」の見出しがある塊では、その見出しより下の教室を
    指定の全時限で使用中とする (見出しは各曜日の塊の左端、帯の中ほどにある)。
  * 教室欄の「※1」は、ページ下部の脚注 (「※1 鶴甲第一キャンパスD棟5階 D503」) の教室を指す。
    脚注から教室を読み取り、「鶴1D503」として出す (toml の foreign で鶴甲第1に振り分ける)。
  * 「Ａ321対面」のように授業形態が教室にくっついた語は、授業形態を取り除く。

source のキー: quarters (既定は3Q,4Q。3Q・4Q専用のPDFでは1つに絞る)
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from ..core import DAYS, Record
from . import _pdf

FORMS = re.compile(r"対面|ハイ[(（][^)）]*[)）]?|遠隔[(（][^)）]*[)）]?|遠隔|オンデマンド|同時双方向")
RENKETSU = re.compile(r"([3-6])・([3-6])限連続")
NOTE = re.compile(r"[※*]\s*(\d)\s*(.*?)([A-Z]\d{3})")


def _n(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def _separators(hs, width):
    ys = sorted(y for y, x0, x1 in hs if x1 - x0 >= 0.9 * width)
    out: list[float] = []
    for y in ys:
        if not out or y - out[-1] > 8:
            out.append(y)
    return out


def _page_lines(ws):
    ws = sorted(ws, key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    out: list[list] = []
    for w in ws:
        cy = (w[1] + w[3]) / 2
        if out and abs((out[-1][0][1] + out[-1][0][3]) / 2 - cy) <= 2.5:
            out[-1].append(w)
        else:
            out.append([w])
    return out


def parse(path: Path, source: dict) -> list[Record]:
    wanted = set(source.get("quarters", ("3Q", "4Q")))
    out: list[Record] = []
    for index, page in _pdf.pages(path):
        ws = _pdf.words(page)
        hs, _ = _pdf.segments(page)
        heads = sorted((w for w in ws if w[4] == "教室"), key=lambda w: w[0])
        if len(heads) < 5:
            continue  # 続きのページ (集中講義の一覧など): 曜日・時限が無い
        top = min(h[1] for h in heads)
        heads = [h for h in heads if abs(h[1] - top) < 4][:5]
        if len(heads) != 5:
            continue
        forms = sorted(
            (w for w in ws if w[4] == "授業形態" and abs(w[1] - top) < 4), key=lambda w: w[0]
        )
        if len(forms) != 5:
            continue

        seps = _separators(hs, page.rect.width)
        labels = [
            (w, int(m.group(1)))
            for w in ws
            if w[0] < 120 and (m := re.fullmatch(r"([1-6])時限", _n(w[4])))
        ]
        bands = []  # (y0, y1, period)
        for w, period in labels:
            cy = (w[1] + w[3]) / 2
            above = [y for y in seps if y < cy]
            below = [y for y in seps if y > cy]
            if above and below:
                bands.append((max(above), min(below), period))
        if not bands:
            continue

        def band_of(cy, bands=bands):
            return next((b for b in bands if b[0] <= cy <= b[1]), None)

        def column_of(x, heads=heads):
            for k in range(5):
                if x <= heads[k][2] + 20:
                    return k
            return 4

        notes = {}
        legend = set()  # 脚注の行そのもの (教室ではない)
        for line in _page_lines(ws):
            text = _n(" ".join(w[4] for w in line))
            m = NOTE.search(text)
            if m and "キャンパス" in text:
                notes["※" + m.group(1)] = m.group(3)
                # 同じ高さに他の列の科目も並ぶので、脚注の語 (キャンパス名を含む語の前後) だけを除く
                kw = next(w for w in line if "キャンパス" in _n(w[4]))
                legend |= {id(w) for w in line if kw[0] - 120 <= w[0] <= kw[2] + 120}

        # 連続授業の見出し: (列, 帯, y, 開始, 終了)
        spans = []
        for w in ws:
            m = RENKETSU.search(_n(w[4]))
            if not m:
                continue
            band = band_of((w[1] + w[3]) / 2)
            if band is None:
                continue
            spans.append((column_of(w[0]), band, w[3], int(m.group(1)), int(m.group(2))))

        for w in ws:
            if id(w) in legend:
                continue
            cx, cy = (w[0] + w[2]) / 2, (w[1] + w[3]) / 2
            col = next(
                (k for k in range(5) if forms[k][0] - 5 <= cx <= heads[k][2] + 15), None
            )
            band = band_of(cy)
            if col is None or band is None or cy < top + 8:
                continue
            text = _n(w[4])
            text = FORMS.sub(" ", text).strip()
            if not text:
                continue
            if text in notes:
                text = "鶴1" + notes[text]
            periods = {band[2]}
            for scol, sband, sy, p0, p1 in spans:
                if scol == col and sband == band and cy > sy - 1:
                    periods |= set(range(p0, p1 + 1))
            for period in sorted(periods):
                for quarter in ("3Q", "4Q"):
                    if quarter in wanted:
                        out.append(Record(DAYS[col], quarter, period, text, f"p{index + 1}"))
    return out
