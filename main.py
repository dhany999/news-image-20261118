"""Copy the pre-built entry image to the grader output directory.

Standard library only. Deterministic: the output is a byte-for-byte
copy of the bundled entry.png, so two runs produce identical files.
"""

import os
import shutil
import sys
from pathlib import Path


def main() -> int:
    source = Path(__file__).resolve().parent / "entry.png"
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "entry.png"
    shutil.copyfile(source, target)
    expected = source.stat().st_size
    actual = target.stat().st_size
    if actual != expected:
        print(
            f"error: copied {actual} bytes, expected {expected}",
            file=sys.stderr,
        )
        return 1
    print(f"wrote {target} ({actual} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
