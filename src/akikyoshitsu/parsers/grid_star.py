"""`grid` に「★ = 鶴甲第二キャンパスの教室」の読み替えを足したもの.

国際人間科学部の時間割は、鶴甲第2キャンパスの教室だけ教室名の前に ★ を付ける
(凡例「★ 鶴甲第二キャンパスの教室」。★ の無い教室は鶴甲第1)。ところが core.split_token は
★ を捨ててしまうので、★B202 と B202 (鶴甲第1の別の部屋) が区別できなくなる。
ここで ★ を source["star_prefix"] (既定 "鶴2") に置き換えてから resolve_rooms に渡す。
toml 側は  strip = "^鶴2"  と  foreign = { "鶴甲第2" = "^鶴2" }  を併記する。
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from ..core import Record
from . import grid


def parse(path: Path, source: dict) -> list[Record]:
    prefix = source.get("star_prefix", "鶴2")
    return [replace(r, token=r.token.replace("★", prefix)) for r in grid.parse(path, source)]
