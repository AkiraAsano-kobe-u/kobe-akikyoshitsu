"""人文学研究科 博士課程後期課程の時間割 (A4 1枚).

載っている科目は「研究科共通科目」の集中講義だけで、毎週の曜日・時限が無い
(「毎週 曜日・時限」の欄は空、「集中」の欄に印がある)。曜日×時限に落とせる情報が無いので
Record は出さない。毎週開講の科目が現れたらここで気付けるよう、PDFに「毎週」欄の
記入 (月〜土 + 数字 + 限) が見つかったら例外にする。
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from ..core import Record
from . import _pdf


def parse(path: Path, source: dict) -> list[Record]:
    for _, page in _pdf.pages(path):
        text = unicodedata.normalize("NFKC", page.get_text())
        if re.search(r"[月火水木金土]曜?\s*日?\s*[1-6]\s*限", text):
            raise ValueError(f"{path.name}: 毎週開講の科目が現れた。パーサを見直すこと")
    return []
