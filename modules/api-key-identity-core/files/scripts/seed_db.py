from __future__ import annotations

import asyncio
import sys
from pathlib import Path


# Ensure `/src` is importable when running `python scripts/seed_db.py`.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from db.seed import seed_from_env  # noqa: E402


async def main() -> None:
    await seed_from_env()


if __name__ == "__main__":
    asyncio.run(main())

