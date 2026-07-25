#!/usr/bin/env python3
"""
Sync one or more Mermaid .mmd source files into marker-wrapped
```mermaid fences in README.md.

For each entry in DIAGRAMS, replaces the content between
    <!-- MERMAID:<key>:START -->
and
    <!-- MERMAID:<key>:END -->
with a fresh ```mermaid code fence built from the given .mmd file.

Exits with code 1 if README.md changed (useful for CI to know whether
a commit is needed), 0 if nothing changed.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"

# Map marker key -> source .mmd file. Add more entries here as you add diagrams.
DIAGRAMS = {
    "flow": REPO_ROOT / "diagrams" / "flow.mmd",
}


def build_block(key: str, mmd_path: Path) -> str:
    source = mmd_path.read_text(encoding="utf-8").rstrip("\n")
    return (
        f"<!-- MERMAID:{key}:START -->\n"
        f"```mermaid\n"
        f"{source}\n"
        f"```\n"
        f"<!-- MERMAID:{key}:END -->"
    )


def main() -> int:
    if not README.exists():
        print(f"README not found at {README}", file=sys.stderr)
        return 2

    text = README.read_text(encoding="utf-8")
    original = text

    for key, mmd_path in DIAGRAMS.items():
        if not mmd_path.exists():
            print(f"Warning: source file missing for '{key}': {mmd_path}", file=sys.stderr)
            continue

        pattern = re.compile(
            rf"<!-- MERMAID:{re.escape(key)}:START -->.*?<!-- MERMAID:{re.escape(key)}:END -->",
            re.DOTALL,
        )
        if not pattern.search(text):
            print(
                f"Warning: no marker pair found for '{key}' "
                f"(expected <!-- MERMAID:{key}:START --> ... <!-- MERMAID:{key}:END -->)",
                file=sys.stderr,
            )
            continue

        text = pattern.sub(build_block(key, mmd_path), text)

    if text != original:
        README.write_text(text, encoding="utf-8")
        print("README.md updated.")
        return 1

    print("README.md already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
