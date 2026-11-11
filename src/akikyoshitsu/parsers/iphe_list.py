"""教養教育院(全学共通授業科目)の一覧型時間割.

「月曜１限」のような見出しの下に、1行1科目で
  時間割コード 科目名 担当教員 教室 [時間割コード 科目名 担当教員 教室]
と並ぶ書式 (左が第3クォーター、右が第4クォーター)。

クォーターの決め方:
  - source["quarters"] が1つだけ (クォーター別ファイル) -> それ
  - 行に 3xxxx と 4xxxx の両方のコード -> 4xxxx より右の教室は後のクォーター
  - コードが片方だけ -> そのコードのクォーター。ただし教室が2つ並んでいれば左右で前後に分ける
  - コードの無い続きの行に教室が1つ -> 両方のクォーターに入れる (空きと誤判定しない側に倒す)
  - source["semester"] = true (セメスター開講の表) -> 常に両方
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from ..core import Record
from . import _pdf

HEADING = re.compile(r"([月火水木金土])曜\s*([0-9・,、]+)限")
CODE = re.compile(r"(?<![0-9A-Za-z])([1-4])[A-Z][0-9A-Z]{3}(?![0-9A-Za-z])")
ROOM = re.compile(r"(?<![0-9A-Za-z\-部舎])[A-Z]\d{3}(?![0-9A-Za-z])")


def parse(path: Path, source: dict) -> list[Record]:
    quarters = list(source.get("quarters", ("3Q", "4Q")))
    first, last = quarters[0], quarters[-1]
    semester = bool(source.get("semester"))
    out: list[Record] = []
    day, periods = None, []
    for index, page in _pdf.pages(path):
        for line in _pdf.lines(page):
            text = unicodedata.normalize("NFKC", "  ".join(w[4] for w in line))
            heading = HEADING.search(text)
            if heading and not CODE.search(text):
                day = heading.group(1)
                periods = [int(x) for x in re.findall(r"\d", heading.group(2))]
                continue
            rooms = [(m.start(), m.group()) for m in ROOM.finditer(text)]
            if not rooms or day is None:
                continue
            codes = [(m.start(), f"{m.group(1)}Q") for m in CODE.finditer(text)]
            early = [p for p, q in codes if q == first]
            late = [p for p, q in codes if q == last and last != first]
            for k, (pos, room) in enumerate(rooms):
                if len(quarters) == 1:
                    qs = quarters
                elif semester:
                    qs = quarters
                elif late and early:
                    qs = [last] if pos > late[0] else [first]
                elif late:
                    qs = [last]
                elif len(rooms) == 2:
                    qs = [first] if k == 0 else [last]
                elif early:
                    qs = [first]
                else:
                    qs = quarters
                for q in qs:
                    for p in periods:
                        out.append(Record(day, q, p, room, f"p{index + 1}: {text[:100]}"))
    return out
