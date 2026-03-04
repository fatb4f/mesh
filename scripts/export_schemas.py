#!/usr/bin/env python3
"""Export canonical SSOT schemas into api/openapi/schemas."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT_DIR = ROOT / "src" / "mesh" / "ssot" / "schemas"
INDEX = SSOT_DIR / "schema.index.json"
OUT_DIR = ROOT / "api" / "openapi" / "schemas"


def main() -> int:
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    schemas = idx.get("schemas", {})
    if not isinstance(schemas, dict) or not schemas:
        raise SystemExit("schema.index.json contains no schemas")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    for name in sorted(schemas.keys()):
        item = schemas[name]
        if not isinstance(item, dict):
            continue
        rel = item.get("path")
        if not isinstance(rel, str) or not rel:
            continue
        src = SSOT_DIR / rel
        if not src.exists():
            raise SystemExit(f"missing schema source: {src}")
        dst = OUT_DIR / src.name
        shutil.copy2(src, dst)
        copied.append(str(dst.relative_to(ROOT)))

    for path in copied:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
