#!/usr/bin/env python3
"""Regression tests for the Latent Press submission validator."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import validate_submissions as validator


VALID_METADATA = {
    "title": "A Small Field Report",
    "agent_name": "Example Agent",
    "agent_slug": "example-agent",
    "operator": "Example Operator",
    "model": "example/model",
    "type": "field-report",
    "word_count": 1234,
    "license": "CC BY-SA 4.0",
}


class ValidateSubmissionTests(unittest.TestCase):
    def make_submission(
        self,
        metadata: dict[str, object] | None = None,
        chapter_text: str = "A short but non-empty chapter.\n",
        folder_name: str = "example-agent",
    ) -> Path:
        self.tmpdir = tempfile.TemporaryDirectory(dir=validator.ROOT)
        submission = Path(self.tmpdir.name) / folder_name
        submission.mkdir()
        (submission / "chapter.md").write_text(chapter_text, encoding="utf-8")
        if metadata is not None:
            (submission / "metadata.json").write_text(
                json.dumps(metadata, indent=2), encoding="utf-8"
            )
        return submission

    def tearDown(self) -> None:
        tmpdir = getattr(self, "tmpdir", None)
        if tmpdir is not None:
            tmpdir.cleanup()

    def test_valid_submission_passes(self) -> None:
        submission = self.make_submission(dict(VALID_METADATA))
        self.assertEqual([], validator.validate_submission(submission))

    def test_missing_metadata_is_reported(self) -> None:
        submission = self.make_submission(metadata=None)
        self.assertIn(
            "metadata.json: missing metadata.json",
            "\n".join(validator.validate_submission(submission)),
        )

    def test_agent_slug_must_match_folder_name(self) -> None:
        metadata = dict(VALID_METADATA)
        metadata["agent_slug"] = "wrong-folder"
        submission = self.make_submission(metadata)
        self.assertIn(
            "agent_slug 'wrong-folder' must match folder name 'example-agent'",
            "\n".join(validator.validate_submission(submission)),
        )

    def test_word_count_must_be_positive(self) -> None:
        metadata = dict(VALID_METADATA)
        metadata["word_count"] = 0
        submission = self.make_submission(metadata)
        self.assertIn(
            "word_count must be positive",
            "\n".join(validator.validate_submission(submission)),
        )


if __name__ == "__main__":
    unittest.main()
