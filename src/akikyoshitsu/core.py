"""パーサ共通の型と、教室名の正規化."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

DAYS = "月火水木金土"
QUARTERS = ("1Q", "2Q", "3Q", "4Q")
# 時限 -> (開始, 終了) HHMM
PERIODS = {1: (850, 1020), 2: (1040, 1210), 3: (1320, 1450), 4: (1510, 1640), 5: (1700, 1830), 6: (1850, 2020)}


@dataclass(frozen=True)
class Record:
    """「この曜日・クォーター・時限に、この教室で授業がある」という1件の事実.

    token は時間割PDFの教室欄に書かれていた文字列そのまま(正規化前)。
    """

    day: str  # "月".."土"
    quarter: str  # "1Q".."4Q" (前期/後期の通し科目はパーサ側で2件に展開する)
    period: int  # 1..6
    token: str
    evidence: str = ""  # デバッグ用: ページ番号や元の行

    def __post_init__(self) -> None:
        if self.day not in DAYS or self.quarter not in QUARTERS or self.period not in PERIODS:
            raise ValueError(f"invalid record: {self}")


# 既定で「教室」とみなす表記。例: B210, LR501, C3-302, A-G03, 5W-301
DEFAULT_ROOM_PATTERN = r"(?:LR|[A-Z])\d{3}|(?:A|C\d|D\d|\d[EW])-[G\d]\d{2}"


def split_token(token: str) -> list[str]:
    """教室欄の文字列を個々の教室表記に分ける ("A-101、A-102" / "B304-306" など)."""
    t = unicodedata.normalize("NFKC", token).replace("★", "")
    out: list[str] = []
    for part in re.split(r"[,、/・\s]+", t):
        part = part.strip("()[]【】")
        if not part:
            continue
        if re.fullmatch(r"\d{3}", part) and out:
            # 「B304・305」「本館102・103」: 棟の表記を前の教室から引き継ぐ
            head = re.fullmatch(r"(.*?)\d{3}", out[-1])
            if head and head.group(1):
                part = head.group(1) + part
        m = re.fullmatch(r"([A-Z]+)(\d{3})-(\d{3})", part)
        if m and int(m.group(2)) < int(m.group(3)) <= int(m.group(2)) + 10:
            out += [f"{m.group(1)}{n}" for n in range(int(m.group(2)), int(m.group(3)) + 1)]
        else:
            out.append(part)
    return out


def resolve_rooms(token: str, source: dict) -> list[tuple[str, str]]:
    """token を (エリア, 教室名) のリストにする。教室と認識できない表記は捨てる.

    source のキー:
      area         既定のエリア名 (例 "鶴甲第1")
      room_pattern 教室とみなす正規表現 (fullmatch)。省略時 DEFAULT_ROOM_PATTERN
      strip        教室名から取り除く接頭辞などの正規表現 (省略可)
      foreign      {エリア名: 正規表現} 他キャンパスの教室を指す表記 (search、strip 前の表記に適用)
      rename       {正規表現: 置換} 教室名の書き換え (re.sub)。エリア判定の後に適用
    """
    pattern = re.compile(source.get("room_pattern", DEFAULT_ROOM_PATTERN))
    out: list[tuple[str, str]] = []
    for part in split_token(token):
        area = source["area"]
        for a, pat in source.get("foreign", {}).items():
            if re.search(pat, part):
                area = a
                break
        if source.get("strip"):
            part = re.sub(source["strip"], "", part)
        for pat, rep in source.get("rename", {}).items():
            part = re.sub(pat, rep, part)
        if pattern.fullmatch(part):
            out.append((area, part))
    return out
