#!/usr/bin/env python3
"""
Add a DOI placeholder to all paper markdown files.

What it does (per file in docs/papers/**/*.md, excluding index.md):
1) Adds `doi:` to YAML front matter right after `authors:` (if missing).
2) Ensures the page header includes a DOI line right after the Authors line:
   **DOI:** {{ page.meta.doi }}

Run from your repo root:
  python3 add_doi_placeholders.py
"""

from pathlib import Path
import re

PAPERS_DIR = Path("docs/papers")
SKIP_FILES = {"index.md"}

# Header lines we expect (from your current template)
AUTHORS_LINE = "**Authors:** {{ page.meta.authors }}  "
DOI_HEADER_LINE = "**DOI:** {{ page.meta.doi }}  "

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)\Z", re.S)


def add_doi_to_front_matter(fm: str) -> tuple[str, bool]:
    """Insert 'doi:' after 'authors:' line if not present."""
    if re.search(r"(?m)^\s*doi\s*:\s*", fm):
        return fm, False

    lines = fm.splitlines()
    out = []
    inserted = False

    for line in lines:
        out.append(line)
        if not inserted and re.match(r"^\s*authors\s*:\s*", line):
            out.append("doi:")  # blank placeholder
            inserted = True

    # If no authors line found, put doi near the top (after title if present)
    if not inserted:
        out2 = []
        inserted2 = False
        for line in out:
            out2.append(line)
            if not inserted2 and re.match(r"^\s*title\s*:\s*", line):
                out2.append("doi:")
                inserted2 = True
        if inserted2:
            return "\n".join(out2), True

        # Worst case: prepend at top
        return "doi:\n" + "\n".join(out), True

    return "\n".join(out), True


def ensure_doi_in_header(body: str) -> tuple[str, bool]:
    """
    Ensure the visible header contains a DOI line after the Authors line.
    We insert right after the Authors line, only if not already present.
    """
    if DOI_HEADER_LINE.strip() in body:
        return body, False

    idx = body.find(AUTHORS_LINE)
    if idx == -1:
        # If header isn't in the expected format, don't risk mangling the page.
        return body, False

    insert_at = idx + len(AUTHORS_LINE)
    new_body = body[:insert_at] + "\n" + DOI_HEADER_LINE + "\n" + body[insert_at:].lstrip("\n")
    return new_body, True


def process_file(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")

    m = FRONT_MATTER_RE.match(text)
    if not m:
        return False, "no front matter"

    fm, body = m.group(1), m.group(2)

    fm2, changed_fm = add_doi_to_front_matter(fm)
    body2, changed_body = ensure_doi_in_header(body)

    if not (changed_fm or changed_body):
        return False, "already ok (or header not matched)"

    new_text = f"---\n{fm2}\n---\n{body2}"
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

        changed, msg = process_file(f)
        if changed:
            updated += 1
            print(f"✅ {f}: {msg}")
        else:
            skipped += 1
            print(f"↪️  {f}: {msg}")

    print(f"\nDone. Updated: {updated}, Skipped: {skipped}")


if __name__ == "__main__":
    main()