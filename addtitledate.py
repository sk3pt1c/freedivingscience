#!/usr/bin/env python3
"""
Add a visible page header to all paper markdown files.

Inserts this block:
# {{ page.meta.title }}

**Authors:** {{ page.meta.authors }}  
**Date:** {{ page.meta.date }}

...right after the YAML front matter ends and before the reading level line.

Run from your repo root:
  python3 add_meta_header.py
"""

from pathlib import Path

PAPERS_DIR = Path("docs/papers")
SKIP_FILES = {"index.md"}  # add more if you want to skip

HEADER_BLOCK = (
    "# {{ page.meta.title }}\n\n"
    "**Authors:** {{ page.meta.authors }}  \n"
    "**Date:** {{ page.meta.date }}\n\n"
)

READING_LEVEL_MARKER = "> **Reading level:**"
HEADER_MARKER = "# {{ page.meta.title }}"


def find_front_matter_end(text: str) -> int | None:
    """
    Returns the index (character offset) just after the closing front-matter delimiter line.
    Expects the file to start with '---' and contain a second '---' on its own line.
    """
    if not text.startswith("---"):
        return None

    # Find the first two delimiter lines that are exactly '---' (ignoring trailing spaces)
    lines = text.splitlines(keepends=True)
    delim_idxs = []
    for i, line in enumerate(lines):
        if line.strip() == "---":
            delim_idxs.append(i)
            if len(delim_idxs) == 2:
                break

    if len(delim_idxs) < 2:
        return None

    # Compute char offset just after the second delimiter line
    end_line_idx = delim_idxs[1]
    return sum(len(l) for l in lines[: end_line_idx + 1])


def process_file(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")

    fm_end = find_front_matter_end(text)
    if fm_end is None:
        return False, "no front matter"

    # Identify where reading level begins (after front matter)
    after_fm = text[fm_end:]
    rl_pos = after_fm.find(READING_LEVEL_MARKER)
    if rl_pos == -1:
        return False, "no reading level marker"

    # Avoid duplicates: if header already exists between front matter and reading level, skip
    between = after_fm[:rl_pos]
    if HEADER_MARKER in between:
        return False, "already has header"

    # Insert header right after front matter end, ensuring exactly one blank line before header
    # and at least one blank line after.
    prefix = text[:fm_end]
    suffix = text[fm_end:]

    # Normalize: if suffix doesn't start with a newline, add one
    if suffix and not suffix.startswith("\n"):
        suffix = "\n" + suffix

    # If there are multiple blank lines immediately after front matter, keep them but ensure
    # we don't stack too many before the header.
    # We'll strip leading newlines in suffix, then add exactly two newlines.
    stripped_suffix = suffix.lstrip("\n")
    new_text = prefix.rstrip("\n") + "\n\n" + HEADER_BLOCK + stripped_suffix

    path.write_text(new_text, encoding="utf-8")
    return True, "updated"


def main():
    if not PAPERS_DIR.exists():
        raise SystemExit(f"Can't find {PAPERS_DIR}. Run this from your MkDocs repo root.")

    md_files = sorted(PAPERS_DIR.rglob("*.md"))
    updated = 0
    skipped = 0

    for f in md_files:
        if f.name in SKIP_FILES:
            skipped += 1
            continue

        changed, reason = process_file(f)
        if changed:
            updated += 1
            print(f"✅ {f}: {reason}")
        else:
            skipped += 1
            print(f"↪️  {f}: {reason}")

    print(f"\nDone. Updated: {updated}, Skipped: {skipped}")


if __name__ == "__main__":
    main()