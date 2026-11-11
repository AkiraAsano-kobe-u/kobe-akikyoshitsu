"""「紙面に実際に見えている文字か」を判定する.

人間発達環境学研究科の時間割PDF (Excel由来) には、白色で描かれて紙面では見えない文字 (消し忘れた旧版の行) が
大量に残っている。pdftotext や get_text("words") はそれも拾うので、そのまま使うと
紙面に無い授業で教室が埋まって見える。ページを描画して、その位置に暗い画素があるかで判定する。
"""
from __future__ import annotations

import pymupdf


class Ink:
    def __init__(self, page, scale: float = 1.5, threshold: int = 170):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), colorspace=pymupdf.csGRAY)
        self.w, self.h, self.s = pix.width, pix.height, pix.samples
        self.scale, self.threshold = scale, threshold

    def visible(self, bbox) -> bool:
        """bbox (x0, y0, x1, y1: pt) の中に、背景より暗い画素があるか (罫線にかからないよう少し内側を見る)."""
        k = self.scale
        x0, x1 = int((bbox[0] + 0.7) * k), int((bbox[2] - 0.7) * k) + 1
        y0, y1 = int((bbox[1] + 1.5) * k), int((bbox[3] - 1.5) * k) + 1
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, self.w), min(y1, self.h)
        if x1 <= x0 or y1 <= y0:
            return True  # 判定できないものは見えていることにする (使用中に倒す)
        s, w, t = self.s, self.w, self.threshold
        return any(s[y * w + x] < t for y in range(y0, y1) for x in range(x0, x1))
