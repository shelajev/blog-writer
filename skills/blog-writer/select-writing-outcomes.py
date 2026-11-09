#!/usr/bin/env python3
"""Select a bounded recent set of persona outcomes for planning."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--content-type", required=True)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    if not 1 <= args.limit <= 10:
        parser.error("--limit must be between 1 and 10")
    try:
        lines = args.ledger.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        print(
            json.dumps(
                {"ok": True, "selected": [], "coverage": {"records": 0, "matching": 0}}
            )
        )
        return 0
    except (OSError, UnicodeError) as exc:
        print(f"cannot read outcome ledger: {exc}", file=sys.stderr)
        return 2
    records = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"invalid outcome ledger line {number}: {exc.msg}", file=sys.stderr)
            return 1
        if not isinstance(value, dict):
            print(
                f"invalid outcome ledger line {number}: expected object",
                file=sys.stderr,
            )
            return 1
        records.append(value)
    matching = [
        record
        for record in records
        if record.get("rhetorical_mode") == args.mode
        or str(record.get("content_type", "")).casefold()
        == args.content_type.casefold()
    ]
    matching.sort(
        key=lambda record: (record.get("date", ""), record.get("work_id", "")),
        reverse=True,
    )
    selected = matching[: args.limit]
    shapes = [
        record["shape"] for record in selected if isinstance(record.get("shape"), dict)
    ]
    print(
        json.dumps(
            {
                "ok": True,
                "query": {
                    "rhetorical_mode": args.mode,
                    "content_type": args.content_type,
                },
                "selected": selected,
                "coverage": {
                    "records": len(records),
                    "matching": len(matching),
                    "selected": len(selected),
                },
                "repeated_shapes": [
                    shape for shape in shapes if shapes.count(shape) > 1
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
