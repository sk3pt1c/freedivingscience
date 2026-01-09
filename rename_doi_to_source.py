#!/usr/bin/env python3
"""
Rename front-matter key `doi:` -> `source:` and update the visible header line.

- Front matter:
  - If file has `doi:` and NOT `source:` -> rename `doi:` to `source:` (keeping any value).
  - If file has BOTH `doi:` and `source:` -> remove the `doi:` line (keeps `source:`).

- Body/header:
  - Replace any of these lines with the new standard line:
      **DOI:** {{ page.meta.doi }}
      **DOI:** {{ page.meta.source }}
      **Source:** {{ page.meta.source }}
    -> **DOI / Source:** {{ page.meta.source }}
  - If the new line already exists, it won't duplicate it.

Run from your repo root:
  python3 rename_doi_to_source.py
"""

from pathlib import Path
import re

PAPERS_DIR = Path("docs/papers")
SKIP_FILES = {"index.md"}

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)\Z", re.S)

# Matches front matter lines
DOI_LINE_RE = re.compile(r"^(\s*)doi\s*:(.*)$", re.IGNORECASE)
SOURCE_LINE_RE = re.compile(r"^(\s*)source\s*:(.*)$", re.IGNORECASE)

# Body/header line patterns (we normalize to the standard line below)
HEADER_CANDIDATES = [
    re.compile(r"^\*\*DOI:\*\*\s*\{\{\s*page\.meta\.doi\s*\}\}\s*$"),
    re.compile(r"^\*\*DOI:\*\*\s*\{\{\s*page\.meta\.source\s*\}\}\s*$"),
    re.compile(r"^\*\*Source:\*\*\s*\{\{\s*page\.meta\.source\s*\}\}\s*$"),
    re.compile(r"^\*\*DOI\s*/\s*Source:\*\*\s*\{\{\s*page\.meta\.doi\s*\}\}\s*$"),
]

STANDARD_HEADER_LINE = "**DOI / Source:** {{ page.meta.source }}  "  # keep Markdown line break


def split_front_matter(text: str):
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return None
    return m.group(1), m.group(2)


def update_front_matter(fm: str):
    lines = fm.splitlines()
    has_source = any(SOURCE_LINE_RE.match(l) for l in lines)
    has_doi = any(DOI_LINE_RE.match(l) for l in lines)

    changed = False
    out = []

    for line in lines:
        m_doi = DOI_LINE_RE.match(line)
        if m_doi:
            if has_source:
                # source already exists -> drop doi line
                changed = True
                continue
            else:
                indent, val = m_doi.group(1), m_doi.group(2)
                out.append(f"{indent}source:{val}")
                changed = True
                continue

        out.append(line)

    return "\n".join(out), changed


def update_body(body: str):
    lines = body.splitlines()

    # If the exact standard line already exists anywhere, we’ll avoid inserting duplicates,
    # but we may still need to remove/replace old variants.
    standard_exists = any(l.strip() == STANDARD_HEADER_LINE.strip() for l in lines)

    changed = False
    new_lines = []

    for line in lines:
        stripped = line.strip()

        # If line is already the standard, keep it (ensure spacing at end)
        if stripped == STANDARD_HEADER_LINE.strip():
            new_lines.append(STANDARD_HEADER_LINE)
            continue

        # Replace any known candidate header lines with the standard line
        if any(pat.match(stripped) for pat in HEADER_CANDIDATES):
            if not standard_exists:
                new_lines.append(STANDARD_HEADER_LINE)
                standard_exists = True
            # Drop the old line
            changed = True
            continue

        # Also catch common variants with trailing two spaces etc.
        # e.g. "**DOI:** {{ page.meta.doi }}  "
        if re.match(r"^\*\*DOI:\*\*\s*\{\{\s*page\.meta\.doi\s*\}\}\s*$", stripped):
            if not standard_exists:
                new_lines.append(STANDARD_HEADER_LINE)
                standard_exists = True
            changed = True
            continue

        if re.match(r"^\*\*DOI:\*\*\s*\{\{\s*page\.meta\.source\s*\}\}\s*$", stripped):
            if not standard_exists:
                new_lines.append(STANDARD_HEADER_LINE)
                standard_exists = True
            changed = True
            continue

        if re.match(r"^\*\*Source:\*\*\s*\{\{\s*page\.meta\.source\s*\}\}\s*$", stripped):
            if not standard_exists:
                new_lines.append(STANDARD_HEADER_LINE)
                standard_exists = True
            changed = True
            continue

        new_lines.append(line)

    return "\n".join(new_lines) + ("\n" if body.endswith("\n") else ""), changed


def process_file(path: Path):
    text = path.read_text(encoding="utf-8")
    parts = split_front_matter(text)
    if not parts:
        return False, "no front matter"

    fm, body = parts

    fm2, fm_changed = update_front_matter(fm)
    body2, body_changed = update_body(body)

    if not (fm_changed or body_changed):
        return False, "already updated"

    path.write_text(f"---\n{fm2}\n---\n{body2}", encoding="utf-8")
    return True, f"updated (front_matter={fm_changed}, body={body_changed})"


def main():
    if not PAPERS_DIR.exists():
        raise SystemExit(f"Can't find {PAPERS_DIR}. Run this from your MkDocs repo root.")

    updated = 0
    skipped = 0

    for md in sorted(PAPERS_DIR.rglob("*.md")):
        if md.name in SKIP_FILES:
            skipped += 1
            continue

        changed, msg = process_file(md)
        if changed:
            updated += 1
            print(f"✅ {md}: {msg}")
        else:
            skipped += 1
            print(f"↪️  {md}: {msg}")

    print(f"\nDone. Updated: {updated}, Skipped: {skipped}")


if __name__ == "__main__":
    main()