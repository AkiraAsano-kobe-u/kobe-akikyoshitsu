"""2026年度後期 文学部・人文学研究科: PDFを目で見て確かめたコマ."""
import pytest

T = "2026b"
A = "文学部"

# (source, 教室, 曜日, 時限)  後期PDFなので 3Q・4Q の両方に入る。コメントはPDFの該当科目
BOTH = [
    ("lit-bachelor", "B133", "月", 1),  # イギリス文学特殊講義 (遠隔(リ))
    ("lit-bachelor", "A221", "月", 2),  # 西洋史演習 藤澤
    ("lit-bachelor", "A422", "月", 3),  # 現代思想演習 / 外書講読
    ("lit-bachelor", "B231", "月", 3),  # 心理学初級実験実習I (3・4限連続)
    ("lit-bachelor", "B231", "月", 4),  # 同上の4限分 (連続授業の見出しによる)
    ("lit-bachelor", "B231", "月", 5),  # 社会学特殊講義 / 比較社会学
    ("lit-bachelor", "B235", "火", 2),  # 国語学演習 池田
    ("lit-bachelor", "B334", "水", 1),  # 西洋史演習 (水1限)
    ("lit-bachelor", "A321", "水", 4),  # 国文学演習(4年) 有澤 (隔週3・4限連続)
    ("lit-bachelor", "C462", "水", 5),  # 社会調査演習I (隔週4・5限連続)
    ("lit-bachelor", "B235", "木", 3),  # 人文学基礎・東洋史学 (「B235対面」と授業形態が付いた表記)
    ("lit-bachelor", "A307", "木", 4),  # 東洋史演習 真下
    ("lit-bachelor", "B232", "木", 5),  # 国語科教育論B
    ("lit-bachelor", "B233", "金", 1),  # 人文学基礎・心理学 / 芸術学
    ("lit-bachelor", "B333", "金", 2),  # 西洋古典語(ラテン語)
    ("lit-bachelor", "B132", "金", 3),  # 美術史調査法 (3・4限連続)
    ("lit-bachelor", "B132", "金", 4),  # 美術史資料演習
    ("lit-bachelor", "C562", "金", 4),  # 地理学実習I
    ("lit-master", "B134", "月", 1),  # 文化社会学演習 / 多文化理解演習
    ("lit-master", "B233", "月", 2),  # ドイツ文学特殊研究V
    ("lit-master", "C133", "月", 3),  # フランス文学演習II
    ("lit-master", "B231", "月", 5),  # 経験社会学特殊研究II
    ("lit-master", "B133", "火", 2),  # 中国現代文学演習II
    ("lit-master", "B333", "水", 2),  # 西洋古代史演習I ほか (結合セル)
    ("lit-master", "B562", "水", 3),  # 西洋美術史演習 / 日本美術史演習
    ("lit-master", "A221", "水", 4),  # フランス文学演習IV (隔週3・4限連続)
    ("lit-master", "C462", "水", 5),  # 社会調査法演習I (隔週4・5限連続)
    ("lit-master", "A321", "木", 1),  # 東洋中世史演習II
    ("lit-master", "C262", "木", 2),  # 理論社会学演習II
    ("lit-master", "B332", "金", 2),  # 認知言語学特殊研究II
]


@pytest.mark.parametrize("quarter", ["3Q", "4Q"])
@pytest.mark.parametrize("source,room,day,period", BOTH)
def test_semester_occupied(occupied, source, room, day, period, quarter):
    assert (A, room, day, quarter, period) in occupied(T, source)


# (source, 教室, 曜日, クォーター, 時限)  クォーター限定のPDF
SINGLE = [
    ("lit-bachelor-3q", "A422", "月", "3Q", 3),  # 現代思想演習
    ("lit-bachelor-3q", "B235", "月", "3Q", 3),  # 中国文学演習
    ("lit-bachelor-3q", "B231", "月", "3Q", 4),  # 心理学初級実験実習I (3・4限連続)
    ("lit-bachelor-3q", "B232", "火", "3Q", 3),  # 東洋史(a) ほか
    ("lit-bachelor-3q", "C562", "火", "3Q", 3),  # 社会学演習(a)
    ("lit-bachelor-3q", "B334", "火", "3Q", 3),  # 日本社会文化論演習
    ("lit-bachelor-3q", "B231", "火", "3Q", 3),  # フランス文学特殊講義
    ("lit-bachelor-3q", "A221", "水", "3Q", 4),  # フランス文学演習 (連続)
    ("lit-bachelor-3q", "D503", "水", "3Q", 3),  # ドイツ語学演習 (※1 -> 鶴甲第1 D503)
    ("lit-bachelor-3q", "B132", "木", "3Q", 1),  # 地域歴史遺産保全活用基礎論B
    ("lit-bachelor-4q", "B235", "木", "4Q", 3),  # 人文学基礎・東洋史学
    ("lit-bachelor-4q", "A321", "木", "4Q", 3),  # 日本史演習(b)
    ("lit-bachelor-4q", "C563", "金", "4Q", 3),  # 地理学演習I(b)
    ("lit-bachelor-4q", "B134", "金", "4Q", 3),  # 人文学基礎・ドイツ文学
    ("lit-bachelor-4q", "B132", "金", "4Q", 4),  # 美術史資料演習
    ("lit-bachelor-4q", "B331", "金", "4Q", 1),  # 高度教養セミナー文学部B(b)
]


@pytest.mark.parametrize("source,room,day,quarter,period", SINGLE)
def test_single_quarter_occupied(occupied, source, room, day, quarter, period):
    area = "鶴甲第1" if room == "D503" else A
    assert (area, room, day, quarter, period) in occupied(T, source)


def test_quarter_limited_pdfs_stay_in_their_quarter(occupied):
    assert {b[3] for b in occupied(T, "lit-bachelor-3q")} == {"3Q"}
    assert {b[3] for b in occupied(T, "lit-bachelor-4q")} == {"4Q"}


def test_footnote_room_goes_to_tsurukabuto(occupied):
    # 「※1 鶴甲第一キャンパスD棟5階 D503」は文学部エリアの教室にしない。水3限だけ
    busy = occupied(T, "lit-bachelor")
    assert {(b[2], b[4]) for b in busy if b[1] == "D503"} == {("水", 3)}
    assert not [b for b in busy if b[1] == "D503" and b[0] == A]


def test_free_slots_stay_free_bachelor(occupied):
    busy = occupied(T, "lit-bachelor")
    assert not [b for b in busy if b[2] == "火" and b[4] == 1]  # 火曜1限は授業なし
    assert not [b for b in busy if b[2] == "金" and b[4] == 5]  # 金曜5限は授業なし
    assert (A, "B232", "金", "3Q", 5) not in busy
    assert (A, "B231", "木", "3Q", 1) not in busy  # 木1限は A321/B132/B135 のみ
    assert (A, "B132", "火", "4Q", 1) not in busy
    assert (A, "B132", "木", "4Q", 5) not in busy


def test_free_slots_stay_free_master(occupied):
    busy = occupied(T, "lit-master")
    assert not [b for b in busy if b[2] == "火" and b[4] == 1]  # 火1限は教員研究室のみ (捨てる)
    assert not [b for b in busy if b[2] == "金" and b[4] == 1]
    assert not [b for b in busy if b[2] == "火" and b[4] == 5]
    assert (A, "B132", "月", "3Q", 5) not in busy
    assert (A, "B231", "月", "4Q", 1) in busy  # 月1限 B231 (西洋近世史特殊研究II) は 4Q にも入る


def test_not_classrooms_are_dropped(occupied):
    rooms = {b[1] for b in occupied(T, "lit-bachelor") | occupied(T, "lit-master")}
    assert all(r[0] in "ABCD" and r[1:].isdigit() for r in rooms), rooms


def test_kodokyoyo(occupied):
    busy = occupied(T, "lit-kodokyoyo")
    assert busy == {
        (A, "B232", "木", "3Q", 2), (A, "B232", "木", "3Q", 4),
        (A, "B232", "木", "4Q", 2), (A, "B232", "木", "4Q", 4),
        (A, "B331", "金", "3Q", 1), (A, "B331", "金", "4Q", 1),
    }  # 3L999 (集中・教室未記載) は載らない


def test_doctor_has_only_intensive_courses(occupied):
    assert occupied(T, "lit-doctor") == set()
