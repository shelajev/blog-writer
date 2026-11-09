#!/usr/bin/env python3
"""Append a validated final/published writing event to a persona outcome ledger."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path


MODES = {"explain", "persuade", "propose", "critique", "narrate", "correspond"}
REGISTERS = {"casual", "peer-professional", "executive-formal"}
ORIGINS = {"human-drafted", "human-rewritten", "assistant-assisted"}
EVENTS = {"final", "published"}


def existing_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"existing ledger line {number} is invalid JSON: {exc.msg}"
            ) from exc
        if not isinstance(value, dict):
            raise ValueError(f"existing ledger line {number} is not an object")
        records.append(value)
    return records


def atomic_write(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(
        prefix=path.name + ".", dir=path.parent, text=True
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            for record in records:
                stream.write(
                    json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
                )
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--persona", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--locator", required=True)
    parser.add_argument("--content-type", required=True)
    parser.add_argument("--mode", required=True, choices=sorted(MODES))
    parser.add_argument("--register", required=True, choices=sorted(REGISTERS))
    parser.add_argument("--language", required=True)
    parser.add_argument("--visibility", required=True, choices=["private", "public"])
    parser.add_argument("--origin", required=True, choices=sorted(ORIGINS))
    parser.add_argument("--event", required=True, choices=sorted(EVENTS))
    parser.add_argument("--opening-mode")
    parser.add_argument("--arc")
    parser.add_argument("--closing-mode")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.persona):
        parser.error("--persona must be lowercase kebab-case")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        parser.error("--date must use YYYY-MM-DD")
    if not re.fullmatch(r"[a-z]{2,3}(?:-[A-Z]{2})?", args.language):
        parser.error("--language must be an ISO-style tag such as en or pt-BR")
    record = {
        "work_id": args.work_id,
        "persona": args.persona,
        "date": args.date,
        "locator": args.locator,
        "content_type": args.content_type,
        "rhetorical_mode": args.mode,
        "register": args.register,
        "language": args.language,
        "visibility": args.visibility,
        "origin": args.origin,
        "event": args.event,
    }
    shape_values = (args.opening_mode, args.arc, args.closing_mode)
    if any(shape_values) and not all(shape_values):
        parser.error(
            "--opening-mode, --arc, and --closing-mode must be supplied together"
        )
    if all(shape_values):
        record["shape"] = {
            "opening_mode": args.opening_mode,
            "arc": args.arc,
            "closing_mode": args.closing_mode,
        }
    try:
        records = existing_records(args.ledger)
        duplicate = next(
            (
                item
                for item in records
                if item.get("work_id") == args.work_id
                and item.get("event") == args.event
                and item.get("persona") == args.persona
            ),
            None,
        )
        if duplicate:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": "outcome event already recorded",
                        "record": duplicate,
                    }
                ),
                file=sys.stderr,
            )
            return 1
        records.append(record)
        atomic_write(args.ledger, records)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"cannot update outcome ledger: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {"ok": True, "ledger": str(args.ledger), "record": record},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
