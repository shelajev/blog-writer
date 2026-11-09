import json
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "select-calibration.py"


def record(identifier, content_type, **overrides):
    value = {
        "id": identifier,
        "text": "A self-contained human passage with enough context for calibration.",
        "source": f"https://example.test/{identifier}",
        "date": "2026-01-01",
        "language": "en",
        "privacy": "public",
        "provenance": "human-authored",
        "rhetorical_mode": "persuade",
        "register": "peer-professional",
        "content_type": content_type,
        "status": "active",
    }
    value.update(overrides)
    return value


class SelectorTests(unittest.TestCase):
    def run_selector(self, records, *extra):
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "corpus.jsonl"
            corpus.write_text(
                "".join(json.dumps(item) + "\n" for item in records),
                encoding="utf-8",
            )
            command = [
                "python3",
                str(SCRIPT),
                "--corpus",
                str(corpus),
                "--mode",
                "persuade",
                "--content-type",
                "conference abstract",
                "--register",
                "peer-professional",
                "--language",
                "en",
                "--visibility",
                "public",
                *extra,
            ]
            return subprocess.run(command, text=True, capture_output=True, check=False)

    def test_empty_corpus_is_unresolved(self):
        result = self.run_selector([])
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["readiness"], "unresolved")
        self.assertEqual(payload["selected"], [])

    def test_ready_selection_prefers_different_content_types(self):
        result = self.run_selector(
            [
                record("new-abstract", "conference abstract", date="2026-03-01"),
                record("old-abstract", "conference abstract", date="2026-02-01"),
                record("linkedin", "LinkedIn post", date="2026-01-01"),
                record("email", "email", date="2025-12-01"),
            ],
            "--limit",
            "2",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["readiness"], "ready")
        self.assertEqual(
            {item["content_type"] for item in payload["selected"][:2]},
            {"LinkedIn post", "email"},
        )

    def test_public_assignment_cannot_retrieve_private_passage(self):
        result = self.run_selector(
            [
                record("public", "blog post"),
                record("private", "email", privacy="private"),
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual([item["id"] for item in payload["selected"]], ["public"])
        self.assertEqual(payload["readiness"], "unresolved")

    def test_other_modes_and_deprecated_passages_do_not_match(self):
        result = self.run_selector(
            [
                record("explanation", "tutorial", rhetorical_mode="explain"),
                record("deprecated", "blog post", status="deprecated"),
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["selected"], [])

    def test_assistant_provenance_is_rejected(self):
        result = self.run_selector(
            [record("assistant", "blog post", provenance="assistant-generated")]
        )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stderr)
        self.assertIn("provenance must be 'human-authored'", payload["errors"][0])

    def test_duplicate_ids_are_rejected(self):
        result = self.run_selector(
            [record("same", "blog post"), record("same", "email")]
        )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stderr)
        self.assertIn("duplicate id", payload["errors"][0])


if __name__ == "__main__":
    unittest.main()
