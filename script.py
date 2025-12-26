from pathlib import Path
import re

papers_dir = Path("docs/papers")
DEFAULT_LEVEL = "beginner"
LEVEL_TAG = f"level-{DEFAULT_LEVEL}"

for md_file in papers_dir.glob("*.md"):
    if md_file.name == "index.md":
        continue

    text = md_file.read_text(encoding="utf-8")

    # ---------- FRONT MATTER ----------
    fm_match = re.search(r"(---.*?---)", text, re.DOTALL)
    if not fm_match:
        print(f"Skipping {md_file.name}: no front-matter")
        continue

    front_matter = fm_match.group(1)
    body = text.replace(front_matter, "").lstrip()

    # Add level to front-matter if missing
    if not re.search(r"^level\s*:", front_matter, re.MULTILINE):
        front_matter = re.sub(
            r"(tags:\n(?:\s+- .*\n)*)",
            r"\1level: " + DEFAULT_LEVEL + "\n",
            front_matter,
            flags=re.MULTILINE
        )

    # Add level tag if missing
    if LEVEL_TAG not in front_matter:
        front_matter = re.sub(
            r"(tags:\n)",
            r"\1  - " + LEVEL_TAG + "\n",
            front_matter,
            count=1
        )

    # ---------- DISPLAY BLOCK ----------
    reading_block = f"> **Reading level:** {DEFAULT_LEVEL.capitalize()}\n\n"

    if reading_block not in body:
        body = re.sub(
            r"(##\s*Why This Matters for Freedivers)",
            reading_block + r"\1",
            body,
            count=1
        )

    # ---------- WRITE BACK ----------
    new_text = f"{front_matter}\n\n{body}"
    md_file.write_text(new_text.strip() + "\n", encoding="utf-8")

    print(f"Updated {md_file.name}")

print("Done.")