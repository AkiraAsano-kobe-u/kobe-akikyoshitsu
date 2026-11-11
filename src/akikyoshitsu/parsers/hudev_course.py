"""人間発達環境学研究科 前期課程「1年履修コース」の時間割 (5〜7限だけの夜間表).

1ページに 前期(第1Q) / 前期(第2Q) / 後期(第3Q) / 後期(第4Q) の4つの表 (各 月〜金) が縦に並び、
左端に「後期（第３Ｑ）」のような縦書きラベルがある。罫線は曜日ラベル列にしかないので、
  - 曜日の帯: 曜日ラベルを挟む水平罫線 (grid._band)
  - クォーター: 5日ぶんの帯ごとに、帯の範囲に入るラベルの数字 (１〜４)
  - 教室列: 「教室」で始まる見出し語の左端から固定幅 (見出しが「教室時間割」と連結している)
で求める。source["period_map"] で列(5,6,7)→標準時限に直す。
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from ..core import DAYS, PERIODS, Record
from . import _pdf
from ._ink import Ink
from ._words import words as _words
from .grid import _band


def parse(path: Path, source: dict) -> list[Record]:
    wanted = set(source.get("quarters", ("3Q", "4Q")))
    pmap = {int(k): v for k, v in source.get("period_map", {}).items()}
    first_col = int(source.get("first_column", 5))  # 左端の列の時限番号
    out: list[Record] = []
    for index, page in _pdf.pages(path):
        ws = _words(page)
        hs, _ = _pdf.segments(page)
        heads = sorted((w for w in ws if unicodedata.normalize("NFKC", w[4]).startswith("教室")), key=lambda w: w[0])
        xs = sorted({round(h[0] / 20) * 20 for h in heads})
        cols = [(x - 14, x + 34) for x in xs]
        if not cols:
            continue
        day_words = sorted((w for w in ws if w[4] in DAYS and w[0] < cols[0][0] - 60), key=lambda w: w[1])
        bands = []
        for d in day_words:
            b = _band(hs, (d[0] + d[2]) / 2, (d[1] + d[3]) / 2)
            if None not in b:
                bands.append((b[0], b[1], d[4]))
        # 5日ぶんずつ (月火水木金) をまとめて1つの表にし、表の範囲内にある数字ラベルでクォーターを決める
        tables = [bands[i : i + 5] for i in range(0, len(bands), 5)]
        labels = [
            (w, unicodedata.normalize("NFKC", w[4]))
            for w in ws
            if w[0] < day_words[0][0] and re.fullmatch(r"[1-4]", unicodedata.normalize("NFKC", w[4]))
        ]
        ink = Ink(page)
        for table in tables:
            top, bottom = table[0][0], table[-1][1]
            qs = [f"{t}Q" for w, t in labels if top <= (w[1] + w[3]) / 2 <= bottom]
            if len(qs) != 1:
                continue  # ラベルが読めない表は使わない (取りこぼしが出るので inspect で必ず確認)
            if qs[0] not in wanted:
                continue
            for word in ws:
                cx, cy = (word[0] + word[2]) / 2, (word[1] + word[3]) / 2
                col = next((first_col + i for i, c in enumerate(cols) if c[0] <= cx <= c[1]), None)
                band = next((b for b in table if b[0] <= cy <= b[1]), None)
                if col is None or band is None or not ink.visible(word[:4]):
                    continue
                for period in pmap.get(col, [col]):
                    if period in PERIODS:
                        out.append(Record(band[2], qs[0], period, word[4], f"p{index + 1}"))
    return out
