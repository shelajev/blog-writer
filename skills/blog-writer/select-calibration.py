#!/usr/bin/env python3
"""Select diverse, privacy-compatible human passages for voice calibration."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


MODES = {"explain", "persuade", "propose", "critique", "narrate", "correspond"}
REGISTERS = {"casual", "peer-professional", "executive-formal"}
PRIVACY = {"public", "private"}
STATUSES = {"active", "deprecated"}
REQUIRED = {
    "id",
    "text",
    "source",
    "date",
    "language",
    "privacy",
    "provenance",
    "rhetorical_mode",
    "register",
    "content_type",
    "status",
}


def valid_language(value: object) -> bool:
    return isinstance(value, str) and bool(
        re.fullmatch(r"[a-z]{2,3}(?:-[A-Z]{2})?", value)
    )


def valid_date(value: object) -> bool:
    return isinstance(value, str) and bool(
        value == "unknown" or re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", value)
    )


def load(path: Path) -> tuple[list[dict], list[str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise RuntimeError(f"cannot read corpus {path}: {exc}") from exc
    records: list[dict] = []
    errors: list[str] = []
    ids: set[str] = set()
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(record, dict):
            errors.append(f"line {number}: record must be an object")
            continue
        missing = sorted(REQUIRED - record.keys())
        if missing:
            errors.append(f"line {number}: missing fields: {', '.join(missing)}")
            continue
        if not all(
            isinstance(record[key], str) and record[key].strip() for key in REQUIRED
        ):
            errors.append(
                f"line {number}: every required field must be a non-empty string"
            )
            continue
        if record["id"] in ids:
            errors.append(f"line {number}: duplicate id {record['id']!r}")
            continue
        if record["privacy"] not in PRIVACY:
            errors.append(f"line {number}: invalid privacy {record['privacy']!r}")
        if record["provenance"] != "human-authored":
            errors.append(f"line {number}: provenance must be 'human-authored'")
        if record["rhetorical_mode"] not in MODES:
            errors.append(
                f"line {number}: invalid rhetorical_mode {record['rhetorical_mode']!r}"
            )
        if record["register"] not in REGISTERS:
            errors.append(f"line {number}: invalid register {record['register']!r}")
        if record["status"] not in STATUSES:
            errors.append(f"line {number}: invalid status {record['status']!r}")
        if not valid_language(record["language"]):
            errors.append(f"line {number}: invalid language {record['language']!r}")
        if not valid_date(record["date"]):
            errors.append(f"line {number}: invalid date {record['date']!r}")
        if any(message.startswith(f"line {number}:") for message in errors):
            continue
        ids.add(record["id"])
        records.append(record)
    return records, errors


def select_diverse(records: list[dict], limit: int, target_type: str) -> list[dict]:
    selected: list[dict] = []
    remaining = sorted(
        records,
        key=lambda record: (
            record["content_type"].casefold() != target_type.casefold(),
            record["date"] != "unknown",
            record["date"],
            record["id"],
        ),
        reverse=True,
    )
    while remaining and len(selected) < limit:
        used_types = {record["content_type"].casefold() for record in selected}
        choice = next(
            (
                record
                for record in remaining
                if record["content_type"].casefold() not in used_types
            ),
            remaining[0],
        )
        selected.append(choice)
        remaining.remove(choice)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--content-type", required=True)
    parser.add_argument("--mode", required=True, choices=sorted(MODES))
    parser.add_argument("--register", required=True, choices=sorted(REGISTERS))
    parser.add_argument("--language", required=True)
    parser.add_argument("--visibility", required=True, choices=sorted(PRIVACY))
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    if not valid_language(args.language):
        parser.error("--language must be an ISO-style tag such as en or pt-BR")
    if not 2 <= args.limit <= 5:
        parser.error("--limit must be between 2 and 5")
    try:
        records, errors = load(args.corpus)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2), file=sys.stderr)
        return 1
    eligible = [
        record
        for record in records
        if record["status"] == "active"
        and record["language"] == args.language
        and record["rhetorical_mode"] == args.mode
        and record["register"] == args.register
        and (args.visibility == "private" or record["privacy"] == "public")
    ]
    selected = select_diverse(eligible, args.limit, args.content_type)
    result = {
        "ok": True,
        "readiness": "ready" if len(selected) >= 2 else "unresolved",
        "query": {
            "content_type": args.content_type,
            "rhetorical_mode": args.mode,
            "register": args.register,
            "language": args.language,
            "visibility": args.visibility,
        },
        "selected": selected,
        "coverage": {
            "records": len(records),
            "eligible": len(eligible),
            "selected": len(selected),
            "distinct_content_types": len(
                {record["content_type"].casefold() for record in selected}
            ),
            "same_as_target": sum(
                record["content_type"].casefold() == args.content_type.casefold()
                for record in selected
            ),
        },
        "creativity_check": "Name a meaningful structural difference the new assignment will retain.",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
