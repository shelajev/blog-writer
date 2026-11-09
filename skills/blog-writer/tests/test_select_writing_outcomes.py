import json
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "select-writing-outcomes.py"


class OutcomeSelectionTests(unittest.TestCase):
    def test_missing_ledger_is_empty_not_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--ledger",
                    str(Path(directory) / "missing.jsonl"),
                    "--mode",
                    "persuade",
                    "--content-type",
                    "conference abstract",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["selected"], [])

    def test_selection_is_bounded_and_matches_mode_or_type(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "outcomes.jsonl"
            records = [
                {
                    "work_id": "a",
                    "date": "2026-01-01",
                    "rhetorical_mode": "persuade",
                    "content_type": "blog post",
                },
                {
                    "work_id": "b",
                    "date": "2026-02-01",
                    "rhetorical_mode": "explain",
                    "content_type": "conference abstract",
                },
                {
                    "work_id": "c",
                    "date": "2026-03-01",
                    "rhetorical_mode": "explain",
                    "content_type": "email",
                },
            ]
            ledger.write_text(
                "".join(json.dumps(item) + "\n" for item in records), encoding="utf-8"
            )
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--ledger",
                    str(ledger),
                    "--mode",
                    "persuade",
                    "--content-type",
                    "conference abstract",
                    "--limit",
                    "1",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["coverage"]["matching"], 2)
            self.assertEqual([item["work_id"] for item in payload["selected"]], ["b"])


if __name__ == "__main__":
    unittest.main()
