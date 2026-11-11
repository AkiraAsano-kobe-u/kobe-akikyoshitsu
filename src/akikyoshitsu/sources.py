"""sources/<学期>/*.toml の読み込みと PDF の取得."""
from __future__ import annotations

import hashlib
import time
import tomllib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
USER_AGENT = "akikyoshitsu/0.1 (unofficial classroom finder for Kobe University students)"


def load_term(term: str, root: Path = ROOT) -> tuple[dict, list[dict]]:
    """(学期の情報, source のリスト) を返す。各 source には defaults が展開済み."""
    directory = root / "sources" / term
    meta = tomllib.loads((directory / "term.toml").read_text(encoding="utf-8"))
    sources: list[dict] = []
    for path in sorted(directory.glob("*.toml")):
        if path.name == "term.toml":
            continue
        doc = tomllib.loads(path.read_text(encoding="utf-8"))
        defaults = doc.get("defaults", {})
        for entry in doc.get("source", []):
            source = {**defaults, **entry, "file": path.name}
            for key in ("foreign", "rename"):  # 表はキーごとに重ねる (source 側が優先)
                if key in defaults or key in entry:
                    source[key] = {**defaults.get(key, {}), **entry.get(key, {})}
            source.setdefault("quarters", list(meta["quarters"]))
            sources.append(source)
    ids = [s["id"] for s in sources]
    duplicated = {i for i in ids if ids.count(i) > 1}
    if duplicated:
        raise ValueError(f"duplicated source id: {sorted(duplicated)}")
    return meta, sources


def fetch(source: dict, term: str, refresh: bool = False, root: Path = ROOT) -> Path:
    """PDF を cache/<学期>/<id>.pdf に取得して、そのパスを返す."""
    path = root / "cache" / term / f"{source['id']}.pdf"
    if path.exists() and not refresh:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    time.sleep(1)  # 大学のサーバーに続けて要求しない
    request = urllib.request.Request(source["url"], headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read()
    if not body.startswith(b"%PDF"):
        raise RuntimeError(f"{source['id']}: PDF ではない応答 ({source['url']})")
    path.write_bytes(body)
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
