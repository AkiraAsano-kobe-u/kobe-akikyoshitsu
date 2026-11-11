"""法学部の後期時間割 (A4横3枚。うち時間割は先頭2枚).

1つの曜日は次の帯でできている:
  1. 見出し行 (「教室」が5つ = 1〜5時限) の下に、セメスター通し(3Q・4Q両方)の科目が並ぶ段
  2. 「3Q」「4Q」の黒い帯 + 見出し行 (「教室」が10 = 時限ごとに 3Q列・4Q列) の下に、クォーター別の段
     (2・3・4年の段と1年の段)

読み方:
  - 1. の段の教室 -> 3Q と 4Q の両方
  - 2. の段で3Q列に入っている教室 -> 3Q。4Q列に入っている教室 -> 4Q。
    ただし科目名の欄が3Q列と4Q列にまたがって (行頭が4Q列より左) いれば
    「【セメスター開講】」の通し科目なので両方 (教室は右端 = 4Q列に書かれる)。
  - 科目名の ①②③④ は対象学年であってクォーターではない。
"""
from __future__ import annotations

from pathlib import Path

from ..core import Record
from . import _pdf, _rokkodai1 as rk

PERIODS = 5
TOL = 4.0  # 教室列は幅6.5ptしかない。教員列は約11pt左


def parse(path: Path, source: dict) -> list[Record]:
    out: list[Record] = []
    for index, page in _pdf.pages(path):
        ws = _pdf.words(page)
        hs, _ = _pdf.segments(page)
        heads = rk.room_header_words(ws)
        if not heads:
            continue
        # 1〜5時限の見出し行 (教室が5つ並ぶ行) と、時限×クォーターの見出し行 (10)
        rows: dict[int, list] = {}
        for h in heads:
            rows.setdefault(round(h[1] / 4), []).append(h)
        singles = [sorted(r, key=lambda h: h[0]) for r in rows.values() if len(r) == PERIODS]
        doubles = [sorted(r, key=lambda h: h[0]) for r in rows.values() if len(r) == 2 * PERIODS]
        if not singles or not doubles:
            continue
        singles.sort(key=lambda r: r[0][1])
        single = singles[0]
        double = doubles[0]
        cols1 = [(h[0] + h[2]) / 2 for h in single]
        cols2 = [(h[0] + h[2]) / 2 for h in double]
        qlabels = [w for w in ws if rk.nfkc(w[4]) in ("3Q", "4Q")]
        # 曜日の帯: 5時限の見出し行から次の見出し行まで。曜日は左端のラベルを上から順に当てる
        days = [c[4] for c in rk.label_chars(page, 60)]
        if len(days) != len(singles):
            raise ValueError(f"law-ug p{index + 1}: 曜日ラベル {days} と見出し行 {len(singles)} 個が合わない")
        # 最後の曜日の下に別の表 (集中講義の「教室・備考」など) があれば、そこまでで切る
        other = [r[0][1] for r in rows.values() if len(r) not in (PERIODS, 2 * PERIODS) and r[0][1] > singles[-1][0][1] + 30]
        starts = [r[0][1] - 3 for r in singles] + [min(other) - 12 if other else page.rect.y1]
        bands = [rk.Band(d, starts[i], starts[i + 1]) for i, d in enumerate(days)]
        for band in bands:
            qy = min((rk.center(w)[1] for w in qlabels if band.has(rk.center(w)[1])), default=None)
            if qy is None:
                continue
            # 各時限の3Q列・4Q列の境界 (3Qと4Qのラベルの中点)
            for w in ws:
                cx, cy = rk.center(w)
                if not band.has(cy) or cy < single[0][1]:
                    continue
                if cy < qy:
                    col = next((i for i, x in enumerate(cols1) if abs(cx - x) <= TOL), None)
                    if col is not None:
                        for q in ("3Q", "4Q"):
                            out.append(Record(band.label, q, col + 1, w[4], f"p{index + 1} single"))
                    continue
                col = next((i for i, x in enumerate(cols2) if abs(cx - x) <= TOL), None)
                if col is None:
                    continue
                period, is_4q = col // 2 + 1, col % 2 == 1
                quarters = ["4Q"] if is_4q else ["3Q"]
                if is_4q:
                    boundary = cols2[col - 1] + 6  # 3Q欄と4Q欄の境
                    line = [v for v in ws if abs(rk.center(v)[1] - cy) <= 3 and v is not w]
                    starts_in_3q = any(cols2[col - 1] - 70 < rk.center(v)[0] < boundary - 3 for v in line)
                    room_in_3q = any(abs(rk.center(v)[0] - cols2[col - 1]) <= TOL for v in line)
                    if starts_in_3q and not room_in_3q:
                        quarters = ["3Q", "4Q"]
                for q in quarters:
                    out.append(Record(band.label, q, period, w[4], f"p{index + 1} {q}列"))
    return out
