"""Verify reader isolation and failed/truncated response handling."""

import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "reader", Path(__file__).parents[1] / "fresh-reader.py"
)
assert spec and spec.loader
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class ReaderTests(unittest.TestCase):
    def run_review(self, result):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "draft.md").write_text("Run the helper. Then deploy.")
            (root / "audience.md").write_text(
                "Developers who know Git; no knowledge of our helper."
            )
            (root / "AGENTS.md").write_text("SECRET_CONTEXT_MUST_NOT_LEAK")
            output = root / "review.md"
            argv = [
                "reader",
                str(root / "draft.md"),
                "--audience",
                str(root / "audience.md"),
                "--output",
                str(output),
            ]
            with (
                patch.dict(os.environ, {"GEMINI_API_KEY": "test-secret"}),
                patch("sys.argv", argv),
                patch.object(
                    reader,
                    "urlopen",
                    return_value=io.BytesIO(json.dumps(result).encode()),
                ) as request,
            ):
                status = reader.main()
                call = request.call_args.args[0]
                body = json.loads(call.data)
                self.assertNotIn("SECRET_CONTEXT_MUST_NOT_LEAK", json.dumps(body))
                self.assertNotIn("test-secret", call.full_url)
                self.assertEqual(set(body), {"contents", "systemInstruction"})
                self.assertEqual(len(body["contents"]), 1)
                return status, output.read_text()

    def test_complete_review_and_isolation(self):
        status, report = self.run_review(
            {
                "modelVersion": "gemini-test",
                "candidates": [
                    {
                        "finishReason": "STOP",
                        "content": {
                            "parts": [
                                {
                                    "text": "NEEDS REVISION: Explain what the helper does."
                                }
                            ]
                        },
                    }
                ],
            }
        )
        self.assertEqual(status, 0)
        self.assertIn("NEEDS REVISION", report)
        self.assertIn("gemini-test", report)

    def test_truncated_is_not_completed(self):
        with self.assertRaises(SystemExit) as error:
            self.run_review(
                {
                    "candidates": [
                        {
                            "finishReason": "MAX_TOKENS",
                            "content": {"parts": [{"text": "partial"}]},
                        }
                    ]
                }
            )
        self.assertEqual(error.exception.code, 1)

    def test_missing_credential(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch(
                "sys.argv",
                [
                    "reader",
                    "draft.md",
                    "--audience",
                    "brief.md",
                    "--output",
                    "review.md",
                ],
            ),
            self.assertRaises(SystemExit) as error,
        ):
            reader.main()
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
