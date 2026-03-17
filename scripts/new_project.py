#!/usr/bin/env python3
"""Generate a new project by copying a template to the target path."""

import argparse
import shutil
import sys
from pathlib import Path

# Ensure repo root is on path so "scripts.module_registry" can be imported
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.module_registry import apply_modules, check_compatibility


def repo_root() -> Path:
    return _REPO_ROOT


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
    parser.add_argument(
        "--modules",
        default="",
        help="Comma-separated optional module names (e.g. webhook_sender).",
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

    module_names = [m.strip() for m in args.modules.split(",") if m.strip()]
    if module_names:
        ok, err = check_compatibility(args.template, module_names)
        if not ok:
            print(f"Error: {err}", file=sys.stderr)
            return 1

    args.path.resolve().mkdir(parents=True, exist_ok=True)
    ignore = shutil.ignore_patterns(
        "__pycache__",
        ".pytest_cache",
        "*.pyc",
        ".git",
    )
    shutil.copytree(template_src, dest, ignore=ignore)
    if module_names:
        apply_modules(dest, args.template, module_names)
    print(f"Created project at {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
