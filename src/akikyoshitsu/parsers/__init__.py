"""時間割PDFのパーサ群.

各パーサは `parse(path: Path, source: dict) -> list[Record]` を公開する。
source は sources/<学期>/*.toml の1エントリ (options もそのまま入っている)。
source["parser"] はこのディレクトリのモジュール名。新しい書式にはモジュールを1つ足すだけでよい。
"""
from __future__ import annotations

from importlib import import_module
from pathlib import Path

from ..core import Record



def parse(path: Path, source: dict) -> list[Record]:
    name = source["parser"]
    try:
        module = import_module(f"{__name__}.{name}")
    except ModuleNotFoundError as error:
        raise KeyError(f"unknown parser {name!r} (source {source.get('id')})") from error
    return module.parse(Path(path), source)
