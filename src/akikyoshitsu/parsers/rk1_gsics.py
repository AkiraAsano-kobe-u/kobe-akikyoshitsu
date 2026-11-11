"""国際協力研究科の後期時間割: 行=曜日(・プログラム)、列=Ⅰ〜Ⅵ時限、各時限は Code|授業科目|教員|Room.

6時限ぶんの「Room」見出しが並ぶページ (前期課程<1> と後期課程) だけを読む。
集中講義のページ (日付と○×で時限を示す) は読まない。
教室は「206」のように建物記号が無い (国際協力研究科棟=第五学舎)・「PR」「SI」「Office」などの略号なので、
rename で読み替える。クォーターの欄は無く、科目名に (4th Q) とあるものだけそのクォーター。
"""
from __future__ import annotations

from pathlib import Path

from ..core import Record
from . import _pdf, _rokkodai1 as rk

TOL = 11.0  # 教室列は見出しの中心から左右この範囲 (教員列は約28pt左、次の時限のコードは約23pt右)
BLOCK = 180.0


def parse(path: Path, source: dict) -> list[Record]:
    out: list[Record] = []
    for index, page in _pdf.pages(path):
        ws = _pdf.words(page)
        hs, _ = _pdf.segments(page)
        heads = rk.top_row(rk.room_header_words(ws))
        if len(heads) == 6:
            out += rk.grid_records(index, page, ws, hs, heads, tol=TOL, block=BLOCK)
    return out
