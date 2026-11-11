"""教室名が隣の語とくっついた単語 (「アクティブライフ教員★B210」) を分けて取り出す.

get_text("words") は空白で語を切るので、教員欄の文字と教室名の間に隙間が無い表では
2つが1語になり、教室列の位置判定からも外れて教室を取りこぼす。
文字ごとの位置 (rawdict) から、「★」「B210」の前後で語を切り直す。
"""
from __future__ import annotations

import re

Word = tuple[float, float, float, float, str]

# 教室名の先頭 (B210 / LR501 / C3-302 / A-G03 / 5W-301) と末尾
ROOM_HEAD = re.compile(r"(?:LR|[A-Z])\d{3}|[A-Z]\d?-[G\d]\d{2}|\d[EW]-\d{3}")
ROOM_TAIL = re.compile(r"(?:[A-Z]\d{3}|-[G\d]\d{2})$")


def _cuts(text: str) -> list[int]:
    cuts = []
    for p in range(1, len(text)):
        prev, cur = text[p - 1], text[p]
        if cur == "★" and prev not in "、,・":
            cuts.append(p)
        elif cur.isascii() and (cur.isupper() or cur.isdigit()) and ROOM_HEAD.match(text, p) and not prev.isascii() and prev not in "★、，・":
            cuts.append(p)
        elif not cur.isascii() and cur not in "、，・★" and ROOM_TAIL.search(text[:p]):
            cuts.append(p)
        elif prev in "、，," and ROOM_TAIL.search(text[: p - 1]) and not ROOM_HEAD.match(text, p):
            cuts.append(p)  # 「A-101、設計基礎C2」: 区切りの後ろが教室でなければそこで切る
    return cuts


def words(page) -> list[Word]:
    out: list[Word] = []
    for block in page.get_text("rawdict")["blocks"]:
        for line in block.get("lines", []):
            chars = [ch for span in line["spans"] for ch in span["chars"]]
            group: list[dict] = []

            def flush():
                if not group:
                    return
                text = "".join(c["c"] for c in group)
                cuts = [0] + _cuts(text) + [len(text)]
                for a, b in zip(cuts, cuts[1:]):
                    part = group[a:b]
                    xs0 = min(c["bbox"][0] for c in part)
                    ys0 = min(c["bbox"][1] for c in part)
                    xs1 = max(c["bbox"][2] for c in part)
                    ys1 = max(c["bbox"][3] for c in part)
                    out.append((xs0, ys0, xs1, ys1, text[a:b]))
                group.clear()

            for ch in chars:
                if ch["c"].isspace():
                    flush()
                else:
                    group.append(ch)
            flush()
    return out
