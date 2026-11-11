"""実PDFに対するテストの共通部品。PDFは配布しないので、cache/ に無ければ skip する.

キャッシュは `uv run akikyoshitsu build 2026b` (または inspect) で作られる。
"""
from __future__ import annotations

import pytest

from akikyoshitsu import parsers, sources
from akikyoshitsu.core import resolve_rooms


@pytest.fixture(scope="session")
def occupied():
    """occupied(term, source_id) -> {(エリア, 教室, 曜日, クォーター, 時限)} を返す関数."""
    cache: dict[tuple[str, str], set] = {}

    def get(term: str, source_id: str) -> set:
        if (term, source_id) not in cache:
            _, entries = sources.load_term(term)
            source = next(s for s in entries if s["id"] == source_id)
            path = sources.ROOT / "cache" / term / f"{source_id}.pdf"
            if not path.exists():
                pytest.skip(f"{path} が無い (akikyoshitsu inspect {term} {source_id} で取得)")
            cache[term, source_id] = {
                (area, room, r.day, r.quarter, r.period)
                for r in parsers.parse(path, source)
                for area, room in resolve_rooms(r.token, source)
            }
        return cache[term, source_id]

    return get
