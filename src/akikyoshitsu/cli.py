"""コマンドライン: akikyoshitsu build / free / room."""
from __future__ import annotations

import argparse
import datetime
import sys

from . import query
from .core import DAYS, PERIODS

NOTE = "注意: 時間割上の授業が無いというだけです。補講・試験・集中講義・課外活動・施錠は反映されていません。"


def _free(args) -> int:
    data = query.load(args.term)
    now = datetime.datetime.now()
    words = args.when
    day = next((w.rstrip("曜") for w in words if w.rstrip("曜") in tuple(DAYS)), DAYS[now.weekday()] if now.weekday() < 6 else None)
    period = next((int(w.rstrip("限")) for w in words if w.rstrip("限").isdigit()), query.period_at(now.time()))
    quarter = next((w.upper() for w in words if w.upper() in data["quarters"]), query.quarter_on(data, now.date()))
    if day is None or period is None or quarter is None:
        print("いまは授業時間外です。曜日・時限・クォーターを指定してください (例: akikyoshitsu free 水 3 3Q)", file=sys.stderr)
        return 2
    if period not in PERIODS:
        print(f"時限は {min(PERIODS)}〜{max(PERIODS)} で指定してください", file=sys.stderr)
        return 2
    print(f"{data['title']} {quarter} {day}曜{period}限 に授業が入っていない教室")
    result = query.free_rooms(data, day, quarter, period)
    for area in sorted(result):
        if args.area and args.area not in area:
            continue
        print(f"\n■ {area}")
        groups: dict[str, list[str]] = {}
        for room, until in result[area]:
            groups.setdefault(query.building(room), []).append(room + (f"(〜{until}限)" if until > period else ""))
        for name in sorted(groups):
            print(f"  {name}: " + " ".join(groups[name]))
    print("\n" + NOTE)
    return 0


def _room(args) -> int:
    data = query.load(args.term)
    found = [(a, r, s) for a, rooms in data["areas"].items() for r, s in rooms.items() if r.upper() == args.name.upper()]
    if not found:
        print(f"{args.name} は時間割に出てこない教室です", file=sys.stderr)
        return 1
    for area, room, slots in found:
        print(f"{area} {room}")
        for quarter in data["quarters"]:
            print(f"  {quarter}")
            for day in DAYS:
                busy = sorted(int(s.rsplit('|', 1)[1]) for s in slots if s.startswith(f"{day}|{quarter}|"))
                if busy:
                    print(f"    {day}: " + " ".join(f"{p}限" for p in busy))
    return 0


def _build(args) -> int:
    from . import build

    data = build.build(args.term, refresh=args.refresh)
    for area, rooms in data["areas"].items():
        print(f"{area}: {len(rooms)} 教室")
    return 0


def _inspect(args) -> int:
    """source を1つずつ解析して、拾った教室と捨てた表記を表示する (パーサ開発用。data/ は書き換えない)."""
    import collections

    from . import parsers, sources
    from .core import resolve_rooms

    _, entries = sources.load_term(args.term)
    for source in entries:
        if args.ids and source["id"] not in args.ids:
            continue
        path = sources.fetch(source, args.term, args.refresh)
        records = parsers.parse(path, source)
        rooms: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
        dropped: collections.Counter[str] = collections.Counter()
        for r in records:
            resolved = resolve_rooms(r.token, source)
            if not resolved:
                dropped[r.token] += 1
            for key in resolved:
                rooms[key].append(f"{r.quarter}{r.day}{r.period}")
        print(f"== {source['id']} ({source['parser']}) {path}: {len(records)} records, {len(rooms)} rooms")
        for (area, room), slots in sorted(rooms.items()):
            print(f"  {area} {room}: {' '.join(sorted(set(slots)))}")
        print(f"  捨てた表記: {dict(dropped.most_common())}")
        if args.verbose:
            for r in records:
                print(f"    {r.quarter} {r.day}{r.period} {r.token!r} [{r.evidence}]")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="akikyoshitsu", description="神戸大学の空き教室を時間割から割り出す (非公式)")
    sub = parser.add_subparsers(dest="command", required=True)
    free = sub.add_parser("free", help="空き教室を表示 (省略時はいま)")
    free.add_argument("when", nargs="*", help="曜日 時限 クォーター (例: 水 3 3Q)。順不同・省略可")
    free.add_argument("--area", help="エリア名で絞る (部分一致)")
    free.add_argument("--term", help="学期 (例: 2026b)。省略時は最新")
    free.set_defaults(func=_free)
    room = sub.add_parser("room", help="教室が使われる時限を表示")
    room.add_argument("name")
    room.add_argument("--term")
    room.set_defaults(func=_room)
    build = sub.add_parser("build", help="時間割PDFを取得・解析して data/ を作り直す")
    build.add_argument("term", help="学期 (例: 2026b)")
    build.add_argument("--refresh", action="store_true", help="キャッシュ済みPDFも取り直す")
    build.set_defaults(func=_build)
    inspect = sub.add_parser("inspect", help="source を個別に解析して結果を表示 (開発用)")
    inspect.add_argument("term")
    inspect.add_argument("ids", nargs="*", help="source の id (省略時は全部)")
    inspect.add_argument("--refresh", action="store_true")
    inspect.add_argument("-v", "--verbose", action="store_true", help="全レコードを表示")
    inspect.set_defaults(func=_inspect)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
