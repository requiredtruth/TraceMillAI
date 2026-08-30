"""Deterministic predicate for the bundled synthetic TraceMillAI demo."""

from __future__ import annotations

import json
from pathlib import Path
import sys


def main() -> int:
    kinds = {
        json.loads(line)["kind"]
        for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    return 7 if {"trigger", "crash"} <= kinds else 0


if __name__ == "__main__":
    raise SystemExit(main())
