import json
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "record-writing-outcome.py"


class OutcomeTests(unittest.TestCase):
    def command(self, ledger, *extra):
        return [
            "python3",
            str(SCRIPT),
            "--ledger",
            str(ledger),
            "--work-id",
            "first-abstract",
            "--persona",
            "oleg-strategic",
            "--date",
            "2026-11-09",
            "--locator",
            "abstracts/first.md",
            "--content-type",
            "conference abstract",
            "--mode",
            "persuade",
            "--register",
            "peer-professional",
            "--language",
            "en",
            "--visibility",
            "public",
            "--origin",
            "assistant-assisted",
            "--event",
            "published",
            *extra,
        ]

    def test_records_assisted_publication_without_promoting_authorship(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "outcomes.jsonl"
            result = subprocess.run(
                self.command(ledger), text=True, capture_output=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            record = json.loads(ledger.read_text(encoding="utf-8"))
            self.assertEqual(record["origin"], "assistant-assisted")
            self.assertNotIn("text", record)

    def test_duplicate_event_is_refused_without_changing_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "outcomes.jsonl"
            first = subprocess.run(self.command(ledger), text=True, capture_output=True)
            before = ledger.read_text(encoding="utf-8")
            second = subprocess.run(
                self.command(ledger), text=True, capture_output=True
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 1)
            self.assertEqual(ledger.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
