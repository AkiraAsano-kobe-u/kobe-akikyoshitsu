"""2026年度後期 鶴甲第2キャンパス (国際人間科学部 発達コミュニティ/環境共生/子ども教育, 人間発達環境学研究科) と
国際文化学研究科: PDFを目で見て確かめたコマ.

国際人間科学部のPDFは、凡例「★ 鶴甲第二キャンパスの教室」の ★ が付いた教室だけが鶴甲第2、無印は鶴甲第1。
人間発達環境学研究科は注意事項により教室欄はすべて鶴甲第2、国際文化学研究科は「キャンパスの記載がない場合、
鶴甲第一キャンパスを指す」。同じ B208 でも ★付きと無印は別の部屋なので、エリアまで含めて照合する。
"""
import pytest

T = "2026b"
T1, T2 = "鶴甲第1", "鶴甲第2"

# (source, エリア, 教室, 曜日, クォーター, 時限)  PDFの該当科目
CASES = [
    # ---- 国際人間科学部 発達コミュニティ学科 ----
    ("fgh-hdc", T2, "B208", "月", "3Q", 1),  # 心の発達と教育３ 岸田 ★B208
    ("fgh-hdc", T2, "B210", "月", "3Q", 2),  # アクティブライフ概論 (教員欄と教室が詰まって1語になっている)
    ("fgh-hdc", T1, "D509", "月", "3Q", 2),  # English for Professional Purposes
    ("fgh-hdc", T1, "D405", "月", "3Q", 3),  # Test Preparation
    ("fgh-hdc", T1, "F102", "月", "3Q", 4),  # 日本文化交流論 (変更前)
    ("fgh-hdc", T2, "B202", "月", "3Q", 4),  # 心の発達と教育１ 坂本 ★B202
    ("fgh-hdc", T1, "F401", "水", "3Q", 1),  # 非言語コミュニケーション論
    ("fgh-hdc", T1, "D406", "水", "3Q", 2),  # World Englishes
    ("fgh-hdc", T2, "C111", "水", "3Q", 4),  # ピアノ演奏演習 ★C111
    ("fgh-hdc", T2, "A137", "金", "3Q", 3),  # 創造の発想とプロセスB ★A137
    ("fgh-hdc", T1, "F101", "金", "3Q", 4),  # Test Preparation
    ("fgh-hdc", T2, "B202", "金", "3Q", 5),  # 地域社会学 ★B202
    ("fgh-hdc", T1, "B109", "水", "4Q", 5),  # フィールドワーク基礎論 (4Qのみ)
    ("fgh-hdc", T2, "F263", "水", "4Q", 4),  # 心理学の基礎と歩み２
    ("fgh-hdc", T2, "B210", "月", "4Q", 2),  # アクティブライフ概論
    # 時間割変更一覧 (2026-11-10版) で PDF より後に変わった教室を使用中にしてある
    ("fgh-hdc", T1, "D505", "金", "3Q", 3),  # Academic Writing(英) ハリソン D506->D505
    ("fgh-hdc", T1, "F301", "月", "4Q", 4),  # 日本文化交流論 F102->F301
    # ---- 環境共生学科 ----
    ("fgh-es", T2, "F151", "月", "3Q", 1),  # 環境資源植物学 ★F151
    ("fgh-es", T2, "B108", "月", "3Q", 2),  # 食環境論B ★B108
    ("fgh-es", T1, "D509", "月", "3Q", 2),  # English for Professional Purposes
    ("fgh-es", T2, "A721", "月", "3Q", 3),  # 数理モデルプログラミング ★A721
    ("fgh-es", T2, "G106", "月", "3Q", 3),  # 環境基礎科学実験C ★G106
    ("fgh-es", T2, "A610", "月", "3Q", 4),  # 環境形成科学演習2C 橋本 ★A610
    ("fgh-es", T2, "B101", "月", "3Q", 4),  # 数学科教育論D ★B101
    ("fgh-es", T2, "B208", "木", "3Q", 1),  # 環境高分子化学 ★B208
    ("fgh-es", T2, "B210", "木", "3Q", 2),  # 環境物理学特別演習2 ★B210
    ("fgh-es", T2, "B102", "木", "3Q", 3),  # 環境応用科学実験B ★B101、★B102
    ("fgh-es", T2, "A712", "木", "3Q", 4),  # 環境形成科学演習2B 前川 ★A712
    ("fgh-es", T2, "F257", "木", "3Q", 5),  # 中等生徒指導論 ★F257
    ("fgh-es", T2, "B101", "金", "3Q", 2),  # 環境形成科学演習2B 松山 ★B101
    ("fgh-es", T1, "F101", "金", "3Q", 3),  # Test Preparation
    ("fgh-es", T2, "G202", "金", "3Q", 4),  # 地球環境学 ★G202
    ("fgh-es", T2, "B201", "金", "3Q", 6),  # 【6時限】環境形成科学演習2B 坂井 ★B201 (5限の列に書かれた6限)
    ("fgh-es", T2, "A637", "木", "4Q", 3),  # 環境応用科学実験D (4Qのみ)
    ("fgh-es", T2, "B201", "木", "4Q", 3),  # ★B201 (4Qのみ)
    ("fgh-es", T2, "A637", "木", "4Q", 4),  # 環境形成科学実験D
    # ---- 子ども教育学科 ----
    ("fgh-ce", T2, "B212", "月", "3Q", 1),  # 初等体育科教育論 ★B212
    ("fgh-ce", T2, "F257", "月", "3Q", 2),  # 初等国語科教育論 ★F257
    ("fgh-ce", T1, "D509", "月", "3Q", 2),  # English for Professional Purposes
    ("fgh-ce", T2, "B201", "月", "3Q", 3),  # 乳児心理学演習 ★B201
    ("fgh-ce", T2, "B210", "月", "3Q", 3),  # 発達障害と共生社会1 ★B210
    ("fgh-ce", T2, "C101", "月", "3Q", 4),  # 初等音楽科教育論 ★C101
    ("fgh-ce", T2, "A325", "月", "3Q", 5),  # 保育内容研究(児童文化と言葉) ★A325
    ("fgh-ce", T2, "B104", "月", "3Q", 5),  # 乳幼児と人間関係 ★B104
    ("fgh-ce", T2, "B104", "金", "3Q", 2),  # 初等家庭科論 ★B104
    ("fgh-ce", T2, "B208", "金", "3Q", 3),  # 教育論 ★B208
    ("fgh-ce", T1, "D510", "金", "3Q", 4),  # Academic Writing(英)
    ("fgh-ce", T2, "F263", "金", "3Q", 5),  # 教職実践演習(幼・小) ★F263
    ("fgh-ce", T2, "B208", "火", "4Q", 1),  # 乳幼児と環境 ★B208 (4Qのみ)
    ("fgh-ce", T2, "B203", "木", "4Q", 3),  # 知的障害支援学 ★B203 (4Qのみ)
    ("fgh-ce", T2, "B203", "木", "4Q", 4),
    # ---- 人間発達環境学研究科 前期課程 (5限は 17:50-19:20 なので 5・6限を埋める) ----
    ("hudev-master", T2, "A303", "月", "3Q", 3),  # 臨床児童心理学特論演習1
    ("hudev-master", T2, "B203", "月", "3Q", 4),  # 心理実践実習I
    ("hudev-master", T2, "A410", "月", "3Q", 5),  # 健康教育学特論演習A
    ("hudev-master", T2, "A410", "月", "3Q", 6),
    ("hudev-master", T2, "A325", "火", "3Q", 1),  # 認知行動支援特論演習1
    ("hudev-master", T2, "A303", "火", "3Q", 3),  # 臨床心理査定演習3
    ("hudev-master", T2, "A325", "火", "3Q", 5),  # 実験社会心理学特論演習I-1
    ("hudev-master", T2, "A404", "水", "3Q", 2),  # 健康行動科学特論演習1
    ("hudev-master", T2, "A303", "木", "3Q", 3),  # 自己形成特論演習1
    ("hudev-master", T2, "A520", "木", "3Q", 4),  # 発達障害臨床学特論演習
    ("hudev-master", T2, "A520", "金", "3Q", 2),  # 教育発達心理学特論演習1
    ("hudev-master", T2, "B206", "月", "3Q", 2),  # 数理認識発達特論演習1 (教育系)
    ("hudev-master", T2, "B201", "金", "4Q", 3),  # 環境光合成科学特論演習2
    ("hudev-master", T2, "G202", "金", "4Q", 2),  # 宇宙環境物理学特論I-2
    ("hudev-master", T2, "B201", "火", "4Q", 1),  # 超分子化学特論演習2
    ("hudev-master", T2, "A712", "水", "4Q", 2),  # 国際社会構造特論演習B
    ("hudev-master", T2, "F153", "木", "4Q", 3),  # 惑星環境物理学特論I-2
    ("hudev-master", T2, "B208", "月", "4Q", 4),  # 都市生態特論演習B
    # ---- 人間発達環境学研究科 後期課程 ----
    ("hudev-doctor", T2, "A303", "月", "3Q", 5),  # 臨床心理実習II-2
    ("hudev-doctor", T2, "A448", "月", "3Q", 5),  # 教育方法学特論II-1
    ("hudev-doctor", T2, "A338", "月", "3Q", 4),  # エンパワメント支援特論II-1
    ("hudev-doctor", T2, "D204", "月", "3Q", 3),  # 身体機能調節特論II-1
    ("hudev-doctor", T2, "A344", "火", "3Q", 1),  # 生涯学習支援特論II-1
    ("hudev-doctor", T2, "A500", "火", "3Q", 3),  # 認知行動支援特論II-1
    ("hudev-doctor", T2, "A322", "火", "3Q", 4),  # 数理認識発達特論II-1
    ("hudev-doctor", T2, "A347", "水", "3Q", 4),  # ジェンダー文化学習特論II-1
    ("hudev-doctor", T2, "A444", "木", "3Q", 5),  # 教育制度特論II-1
    ("hudev-doctor", T2, "A522", "金", "3Q", 1),  # 教育発達心理学特論II-1
    ("hudev-doctor", T2, "F151", "水", "3Q", 2),  # 子ども音楽表現特論II-1
    ("hudev-doctor", T2, "E452", "木", "4Q", 3),  # 行動適応特論II-2
    ("hudev-doctor", T2, "E455", "木", "4Q", 5),  # スポーツジェロントロジー特論II-2
    ("hudev-doctor", T2, "A523", "月", "4Q", 4),  # 食環境学特論II-B
    ("hudev-doctor", T2, "A739", "火", "4Q", 5),  # 応用統計解析特論2
    # ---- 人間発達環境学研究科 前期課程1年履修コース (5〜7限、7限は表現できず捨てる) ----
    ("hudev-master1", T2, "A410", "月", "3Q", 5),  # 健康教育学特論演習A
    ("hudev-master1", T2, "A410", "月", "3Q", 6),
    ("hudev-master1", T2, "A347", "水", "3Q", 6),  # ジェンダー・コミュニティ支援論1
    ("hudev-master1", T2, "A410", "月", "4Q", 5),  # 健康教育学特論演習B
    ("hudev-master1", T2, "A347", "水", "4Q", 6),  # ジェンダー・コミュニティ支援論2
    # ---- 国際文化学研究科 (キャンパスの記載が無ければ鶴甲第1; 後期は3Q・4Q両方) ----
    ("cla-master", T1, "L204", "月", "3Q", 2),  # 異文化関係論演習
    ("cla-master", T1, "F501", "月", "3Q", 2),  # ITコミュニケーション論演習
    ("cla-master", T1, "D603", "月", "3Q", 2),  # 第二言語運用論特殊講義
    ("cla-master", T1, "D505", "月", "3Q", 3),  # アカデミック・コミュニケーション(英語)
    ("cla-master", T1, "D507", "月", "3Q", 3),  # 外国語教育システム論演習
    ("cla-master", T1, "D504", "月", "3Q", 4),  # 外国語教育システム論演習
    ("cla-master", T1, "L204", "月", "3Q", 4),  # 民族学特殊講義
    ("cla-master", T1, "L205", "火", "3Q", 2),  # 越境社会共生論特殊講義
    ("cla-master", T1, "D405", "火", "3Q", 2),  # 外国語教育システム論演習
    ("cla-master", T1, "L206", "火", "3Q", 3),  # 東アジア社会文化論特殊講義
    ("cla-master", T1, "D615", "火", "3Q", 3),  # 外国語教育コンテンツ論演習
    ("cla-master", T1, "B301", "火", "3Q", 4),  # 非言語コミュニケーション論特殊講義
    ("cla-master", T1, "F102", "火", "4Q", 4),  # 異文化コミュニケーション論特殊講義 (後期 = 4Qにも入る)
    ("cla-master", T1, "F101", "火", "3Q", 5),  # 言語行動科学論特殊講義
    ("cla-master", T1, "L202", "火", "4Q", 5),  # 文化環境形成論特殊講義
    ("cla-master", T1, "B305", "木", "3Q", 4),  # ヨーロッパ・アメリカ文化論演習 「B304」の下の行に「-306」と折り返し
    ("cla-master", T1, "B306", "木", "4Q", 4),
    ("cla-doctor", T1, "D507", "水", "3Q", 3),  # 言語対照基礎論特別演習 (D後期)
    ("cla-doctor", T1, "D507", "水", "4Q", 3),
]


@pytest.mark.parametrize("source,area,room,day,quarter,period", CASES)
def test_occupied(occupied, source, area, room, day, quarter, period):
    assert (area, room, day, quarter, period) in occupied(T, source)


# PDFに何も書かれていない (または別の教室が書かれている) コマ
NEGATIVE = [
    ("fgh-hdc", T2, "F263", "水", "3Q", 3),  # F263 は水曜2限と4限だけ
    ("fgh-hdc", T1, "B202", "月", "3Q", 4),  # 月4の B202 は ★付き(鶴甲第2)。鶴甲第1の B202 ではない
    ("fgh-hdc", T2, "C101", "水", "4Q", 3),  # サウンドデザインは3Qだけ
    ("fgh-hdc", T2, "B208", "月", "4Q", 1),  # 心の発達と教育３は3Qだけ
    ("fgh-hdc", T2, "B210", "月", "3Q", 1),  # B210 は2限
    ("fgh-es", T2, "B201", "金", "3Q", 5),  # ★B201 は【6時限】の行 (6限)
    ("fgh-es", T2, "A610", "月", "3Q", 3),  # A610 は月4
    ("fgh-ce", T2, "F257", "月", "3Q", 1),
    ("fgh-ce", T2, "A325", "月", "3Q", 4),  # A325 は5限
    ("fgh-ce", T2, "B201", "月", "3Q", 5),
    ("hudev-master", T2, "A303", "月", "3Q", 1),  # 白文字で残っている消し忘れ (3D632) は紙面に見えない
    ("hudev-master", T2, "A303", "月", "3Q", 2),  # 同 (3D609)
    ("hudev-master", T2, "G202", "水", "4Q", 1),  # 環境基礎生命科学A-2 は3Qだけ
    ("hudev-master", T2, "B203", "月", "4Q", 3),
    ("hudev-doctor", T2, "A500", "火", "3Q", 2),  # 認知行動支援特論II-1 の2限は白文字の消し忘れ
    ("hudev-doctor", T2, "A310", "月", "3Q", 1),  # 心理療法特論II-1 は白文字 (→R8～ 廃止)
    ("hudev-master1", T2, "B210", "木", "3Q", 6),  # ESD研究は白文字の消し忘れ
    ("hudev-master1", T2, "A347", "水", "3Q", 5),  # A347 は6限
    ("hudev-master1", T2, "A347", "木", "3Q", 6),  # 木曜の A347 は7限 (21:10-) で、時限として表現しない
    ("cla-master", T1, "L204", "月", "3Q", 3),
    ("cla-master", T1, "B301", "火", "3Q", 2),
    ("cla-doctor", T1, "D507", "水", "3Q", 2),
    ("cla-doctor", T1, "D507", "水", "3Q", 4),
]


@pytest.mark.parametrize("source,area,room,day,quarter,period", NEGATIVE)
def test_free(occupied, source, area, room, day, quarter, period):
    assert (area, room, day, quarter, period) not in occupied(T, source)


def test_no_rooms_without_classroom_cells(occupied):
    # 国際文化学研究科の月曜1限・5限、環境共生学科の月曜5限は教室欄が空か「研究室」だけ
    assert not [b for b in occupied(T, "cla-master") if b[2] == "月" and b[4] in (1, 5)]
    assert not [b for b in occupied(T, "fgh-es") if b[2] == "月" and b[3] == "3Q" and b[4] == 5]
    # 国際文化学研究科 博士後期の D後期 の表には教室が1つしか無い (【D前期】は対象外)
    assert {b[:2] for b in occupied(T, "cla-doctor")} == {(T1, "D507")}


def test_star_decides_campus(occupied):
    # 国際人間科学部の3PDF: ★付きの教室は鶴甲第2、無印は鶴甲第1。鶴甲第1に出てよい教室は無印の表記だけ
    unmarked = {"B109", "C301", "D405", "D406", "D503", "D504", "D505", "D506", "D509", "D510", "D512", "F101", "F102", "F301", "F401", "K502"}
    for source in ("fgh-hdc", "fgh-es", "fgh-ce"):
        busy = occupied(T, source)
        assert {b[1] for b in busy if b[0] == T1} <= unmarked, source
        assert not {b[1] for b in busy if b[0] == T1} & {"F257", "F263", "B106", "B108", "C101", "C111"}, source
        assert all(b[1] not in {"D405", "K502", "F101"} for b in busy if b[0] == T2), source
    # 大学院: 研究科は鶴甲第2、国際文化学研究科は鶴甲第1だけ
    for source in ("hudev-master", "hudev-doctor", "hudev-master1"):
        assert {b[0] for b in occupied(T, source)} == {T2}
    assert {b[0] for b in occupied(T, "cla-master")} == {T1}
