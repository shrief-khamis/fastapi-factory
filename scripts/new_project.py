#!/usr/bin/env python3
"""Generate a new project by copying a template to the target path."""

import argparse
import shutil
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy a template to a new project directory.",
    )
    parser.add_argument(
        "--template",
        required=True,
        help="Template name (e.g. async_io_api, celery_job_api).",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Project directory name (e.g. my-api).",
    )
    parser.add_argument(
        "--path",
        default=".",
        type=Path,
        help="Parent path for the new project (default: current directory).",
    )
    args = parser.parse_args()

    root = repo_root()
    templates_dir = root / "templates"
    template_src = templates_dir / args.template
    dest = args.path.resolve() / args.name

    if not template_src.is_dir():
        print(f"Error: template '{args.template}' not found at {template_src}", file=sys.stderr)
        return 1

    if dest.exists():
        print(f"Error: destination already exists: {dest}", file=sys.stderr)
        return 1

    args.path.resolve().mkdir(parents=True, exist_ok=True)
    ignore = shutil.ignore_patterns(
        "__pycache__",
        ".pytest_cache",
        "*.pyc",
        ".git",
    )
    shutil.copytree(template_src, dest, ignore=ignore)
    print(f"Created project at {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
