"""2026年度後期 工学部キャンパス: PDFを目で見て確かめたコマ."""
import pytest

T = "2026b"

# (source, 教室, 曜日, クォーター, 時限)  PDFの該当科目
CASES = [
    ("csi-bachelor", "J202", "月", "3Q", 1),  # 人工知能1
    ("csi-bachelor", "LR501", "月", "3Q", 1),  # 制御工学2
    ("csi-bachelor", "J301", "月", "3Q", 2),  # ソフトウェア工学1
    ("csi-bachelor", "LR501", "月", "3Q", 3),  # システムモデル
    ("csi-bachelor", "J202", "月", "4Q", 4),  # 代数・幾何演習2 / 解析演習2
    ("csi-bachelor", "LR501", "火", "3Q", 1),  # データ解析
    ("csi-bachelor", "J202", "火", "3Q", 2),  # 応用解析
    ("csi-bachelor", "C3-302", "水", "3Q", 2),  # 計算論
    ("csi-bachelor", "J301", "水", "3Q", 1),  # システム情報学応用
    ("eng-mm", "LR501", "月", "3Q", 2),  # 製造プロセス工学I
    ("eng-mm", "C4-301", "月", "3Q", 1),  # エネルギー変換工学 (3年)
    ("eng-mm", "C1-301", "月", "3Q", 2),  # 塑性力学 (3年)
    ("eng-cs", "J202", "月", "3Q", 2),  # HPC
    ("eng-master", "C1-201", "月", "3Q", 2),  # 鋼架構論1
    ("csi-master", "LR201", "月", "3Q", 3),  # システム計測特論2 (後期)
    # 教室名が教員名などと1語にくっついているコマ (独立レビューで読み落としが見つかった)
    ("eng-aa", "A-101", "金", "3Q", 3),  # 設計基礎A2 「A-101、設計基礎A2」
    ("eng-aa", "A-102", "金", "3Q", 4),
    ("eng-aa", "A-101", "水", "4Q", 3),  # 設計基礎C2
    ("eng-ee", "LR301", "月", "3Q", 4),  # フーリエ解析 「太田（快）LR301」
    ("eng-ee", "C1-301", "金", "3Q", 4),  # 集積回路工学 「中島・井上C1-301」
    ("eng-ee", "C1-301", "金", "4Q", 5),
    ("eng-ee", "C3-302", "火", "4Q", 5),
    ("eng-mm", "C4-201", "火", "3Q", 1),  # 機械創造設計プロジェクトI 「横小路・磯野C4-201」
    ("eng-mm", "C3-302", "金", "3Q", 2),
    ("eng-mm", "3E-304", "金", "4Q", 3),  # 「本間･グォン3E-304」
]


@pytest.mark.parametrize("source,room,day,quarter,period", CASES)
def test_occupied(occupied, source, room, day, quarter, period):
    assert ("工学部", room, day, quarter, period) in occupied(T, source)


def test_free_slots_stay_free(occupied):
    # システム情報学部の時間割で、月曜5限と金曜3限以降に J202 の授業は無い
    busy = occupied(T, "csi-bachelor")
    assert ("工学部", "J202", "月", "3Q", 5) not in busy
    assert not [b for b in busy if b[1] == "J202" and b[2] == "金" and b[4] >= 3]


def test_every_room_written_on_the_page_is_read(occupied):
    """ページに書かれた工学部棟の教室は、必ずどこかのコマとして読まれている (読み落とし=空きの誤表示)."""
    import re

    import pymupdf

    from akikyoshitsu import sources

    written = re.compile(r"LR\d{3}|[AC]\d?-[G\d]\d{2}|\d[EW]-\d{3}")
    for source in ("eng-aa", "eng-ce", "eng-ee", "eng-mm", "eng-cx", "eng-cs"):
        rooms = {b[1] for b in occupied(T, source) if b[0] == "工学部"}
        text = pymupdf.open(sources.ROOT / "cache" / T / f"{source}.pdf")[0].get_text()
        assert set(written.findall(text)) <= rooms, source
