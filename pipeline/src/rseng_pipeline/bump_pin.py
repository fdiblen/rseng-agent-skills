"""Point upstream.lock at a new upstream commit.

Usage: python -m rseng_pipeline.bump_pin <commit-sha>
The caller is responsible for refetching the cache and regenerating
artifacts afterwards (the sync workflow does exactly that).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def bump(lock_path: Path, new_commit: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", new_commit):
        raise SystemExit(f"not a full commit sha: {new_commit!r}")
    text = lock_path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'commit = "[0-9a-f]{40}"', f'commit = "{new_commit}"', text
    )
    if count != 1:
        raise SystemExit(f"expected exactly one commit line, found {count}")
    lock_path.write_text(updated, encoding="utf-8")


def main() -> None:
    pipeline_dir = Path(__file__).resolve().parents[2]
    bump(pipeline_dir / "upstream.lock", sys.argv[1])
    print(f"lock now pins {sys.argv[1][:8]}")


if __name__ == "__main__":
    main()
