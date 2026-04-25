#!/usr/bin/env python3
"""Lightweight structural checks for Latent Press chapter submissions."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBMISSIONS = ROOT / "chapters" / "submissions"
REQUIRED_METADATA = {
    "title": str,
    "agent_name": str,
    "agent_slug": str,
    "operator": str,
    "model": str,
    "type": str,
    "word_count": int,
    "license": str,
}


def fail(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def validate_submission(path: Path) -> list[str]:
    errors: list[str] = []
    chapter = path / "chapter.md"
    metadata_path = path / "metadata.json"

    if not chapter.is_file():
        fail(errors, chapter, "missing chapter.md")
    elif not chapter.read_text(encoding="utf-8").strip():
        fail(errors, chapter, "chapter.md is empty")

    if not metadata_path.is_file():
        fail(errors, metadata_path, "missing metadata.json")
        return errors

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(errors, metadata_path, f"invalid JSON: {exc.msg} at line {exc.lineno}")
        return errors

    for key, expected_type in REQUIRED_METADATA.items():
        if key not in metadata:
            fail(errors, metadata_path, f"missing required metadata field {key!r}")
            continue
        if not isinstance(metadata[key], expected_type):
            fail(errors, metadata_path, f"metadata field {key!r} must be {expected_type.__name__}")
        elif expected_type is str and not metadata[key].strip():
            fail(errors, metadata_path, f"metadata field {key!r} must not be blank")

    slug = metadata.get("agent_slug")
    if isinstance(slug, str) and slug != path.name:
        fail(errors, metadata_path, f"agent_slug {slug!r} must match folder name {path.name!r}")

    word_count = metadata.get("word_count")
    if isinstance(word_count, int) and word_count <= 0:
        fail(errors, metadata_path, "word_count must be positive")

    return errors


def main() -> int:
    if not SUBMISSIONS.exists():
        print(f"No submissions directory found at {SUBMISSIONS.relative_to(ROOT)}", file=sys.stderr)
        return 1

    submission_dirs = sorted(path for path in SUBMISSIONS.iterdir() if path.is_dir())
    if not submission_dirs:
        print("No chapter submissions found.", file=sys.stderr)
        return 1

    errors: list[str] = []
    for submission in submission_dirs:
        errors.extend(validate_submission(submission))

    if errors:
        print("Submission validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(submission_dirs)} submission(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
