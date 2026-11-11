"""2026年度後期 全学共通授業科目: 見出しが2行に分かれた実験科目と、他キャンパスの教室."""
import pytest

T = "2026b"

CASES = [
    # 「火曜」「3限~4限」と2行に分かれた見出し
    ("iphe-chemistry", "鶴甲第1", "C220", "火", "3Q", 3),  # 化学実験1
    ("iphe-chemistry", "鶴甲第1", "C220", "火", "4Q", 4),  # 化学実験2
    ("iphe-chemistry", "鶴甲第1", "C220", "木", "3Q", 4),
    ("iphe-physics", "鶴甲第1", "C401", "水", "3Q", 3),  # 物理学実験 初回~3回目
    ("iphe-biology", "鶴甲第1", "C510", "月", "3Q", 4),  # 生物学実験
    ("iphe-chemistry", "鶴甲第1", "B201", "月", "3Q", 1),  # 基礎物理化学1
    # 「第5学舎208教室」は六甲台第1
    ("iphe-kyouyou-kouki", "六甲台第1", "第五学舎208", "水", "3Q", 2),  # 国際協力アクティブ・ラーニングC
    ("iphe-kyouyou-kouki", "六甲台第1", "第五学舎201", "木", "4Q", 1),
]


@pytest.mark.parametrize("source,area,room,day,quarter,period", CASES)
def test_occupied(occupied, source, area, room, day, quarter, period):
    assert (area, room, day, quarter, period) in occupied(T, source)


def test_lab_is_not_attached_to_the_previous_heading(occupied):
    busy = occupied(T, "iphe-chemistry")
    assert ("鶴甲第1", "C220", "月", "3Q", 1) not in busy  # 以前は直前の見出し「月曜1限」に付いていた
