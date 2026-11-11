"""経営学研究科(本科履修コース)の後期時間割: 行=曜日、列=1〜6時限、各時限は 申請コード|授業科目|担当|教室.

クォーターの欄は無い。科目名に【3Qのみ開講】【4Qのみ開講】【3Qのみ】とあるものだけそのクォーター、
他は 3Q と 4Q の両方。ページ2の「第5群科目 (学部授業の読替科目)」は
「月2 ゲーム理論研究 安部 Ⅰ102 3B305」のような1行1科目 (セメスター科目なので両クォーター)。
"""
from __future__ import annotations

import re
from pathlib import Path

from ..core import Record
from . import _pdf, _rokkodai1 as rk

TOL = 7.0  # 教室列は見出しの中心から左右この範囲 (次の時限の申請コードは約13pt右)
BLOCK = 88.0  # 1時限ぶんの欄の幅 (科目名の注記を探す範囲)


def parse(path: Path, source: dict) -> list[Record]:
    out: list[Record] = []
    for index, page in _pdf.pages(path):
        ws = _pdf.words(page)
        hs, _ = _pdf.segments(page)
        heads = rk.top_row(rk.room_header_words(ws))
        if len(heads) == 6:
            out += rk.grid_records(index, page, ws, hs, heads, tol=TOL, block=BLOCK)
        else:
            out += _group5(index, page)
    return out


def _group5(index, page) -> list[Record]:
    out: list[Record] = []
    for line in _pdf.lines(page):
        first = rk.nfkc(line[0][4])
        m = re.fullmatch(r"([月火水木金土])([1-6])", first)
        if not m:
            continue
        for w in line[1:]:
            for token in rk.expand_rooms(w[4]):
                for q in ("3Q", "4Q"):
                    out.append(Record(m.group(1), q, int(m.group(2)), token, f"p{index + 1} 第5群"))
    return out
