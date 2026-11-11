"""文学部 高度教養科目の一覧表 (1科目1行、列: コード・科目名・教員・単位・教室・形態・開講期・曜日時限 ...).

行は左端の時間割コード (3L122 など) の位置で区切る。行の中の
  * 教室 (「教室」列)
  * 開講期: 3Q -> 3Q / 4Q -> 4Q / 後期 -> 3Q と 4Q の両方 / 集中 -> 曜日時限が無いので出さない
  * 曜日・時限等: 「木曜2限」のような記述 (複数行あり)
から Record を作る。クォーターが読み取れない行は両方のクォーターに入れる。
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from ..core import Record
from . import _pdf


def _n(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def parse(path: Path, source: dict) -> list[Record]:
    wanted = set(source.get("quarters", ("3Q", "4Q")))
    out: list[Record] = []
    for index, page in _pdf.pages(path):
        ws = _pdf.words(page)
        head = {w[4]: w for w in ws if w[4] in ("教室", "曜日・時限等", "使用言語")}
        if len(head) < 3:
            continue
        room_x0, room_x1 = head["教室"][0] - 10, head["教室"][2] + 10
        slot_x0, slot_x1 = head["曜日・時限等"][0] - 10, head["使用言語"][0] - 5
        top = head["教室"][3]
        codes = sorted(
            (w for w in ws if w[0] < 100 and w[1] > top and re.fullmatch(r"[34]L\d{3}", _n(w[4]))),
            key=lambda w: w[1],
        )
        mids = [(w[1] + w[3]) / 2 for w in codes]
        for k, code in enumerate(codes):
            lo = (mids[k - 1] + mids[k]) / 2 if k else top
            hi = (mids[k] + mids[k + 1]) / 2 if k + 1 < len(codes) else 1e9
            row = [w for w in ws if lo <= (w[1] + w[3]) / 2 < hi]
            rooms = [w[4] for w in row if room_x0 <= (w[0] + w[2]) / 2 <= room_x1]
            slots = []
            for w in row:
                if slot_x0 <= w[0] <= slot_x1:
                    m = re.fullmatch(r"([月火水木金土])曜([1-6])限", _n(w[4]))
                    if m:
                        slots.append((m.group(1), int(m.group(2))))
            period_words = {_n(w[4]) for w in row if 520 <= w[0] <= slot_x0 + 10}
            if "集中" in period_words and "後期" not in period_words:
                continue  # 集中講義のみ: 曜日時限が無い
            quarters = [q for q in ("3Q", "4Q") if q in period_words]
            if not quarters:
                quarters = ["3Q", "4Q"]  # 後期、または読み取れない
            for room in rooms:
                for day, period in slots:
                    for quarter in quarters:
                        if quarter in wanted:
                            out.append(Record(day, quarter, period, room, f"p{index + 1} {_n(code[4])}"))
    return out
