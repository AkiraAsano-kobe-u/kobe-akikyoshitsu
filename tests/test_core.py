from akikyoshitsu.core import resolve_rooms, split_token

ENG = {"area": "工学部", "strip": "^鶴1", "foreign": {"鶴甲第1": r"^(鶴1)?[BK]\d{3}$"}}


def test_split_token():
    assert split_token("A-101、A-102") == ["A-101", "A-102"]
    assert split_token("B304-306") == ["B304", "B305", "B306"]
    assert split_token("★F263") == ["F263"]
    assert split_token("C3-302") == ["C3-302"]


def test_resolve_rooms_default_area():
    assert resolve_rooms("LR501", ENG) == [("工学部", "LR501")]
    assert resolve_rooms("C4-301,", ENG) == [("工学部", "C4-301")]


def test_resolve_rooms_other_campus():
    assert resolve_rooms("鶴１B110", ENG) == [("鶴甲第1", "B110")]
    assert resolve_rooms("K501", ENG) == [("鶴甲第1", "K501")]


def test_resolve_rooms_drops_non_rooms():
    for token in ("研究室", "遠隔", "情報知能", "(Research", "教養科目"):
        assert resolve_rooms(token, ENG) == []


def test_rename():
    source = {"area": "X", "room_pattern": r"本館\d{3}", "rename": {r"^I-?": "本館"}}  # NFKC で Ⅰ は I になる
    assert resolve_rooms("Ⅰ-102", source) == [("X", "本館102")]


def test_split_token_carries_building_prefix():
    assert split_token("B304・305") == ["B304", "B305"]
    assert split_token("C3-302・303") == ["C3-302", "C3-303"]
    assert split_token("206") == ["206"]  # 前の教室が無ければそのまま
