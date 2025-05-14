import os

docs_folder = 'docs'
exclude_files = ['index.md', 'about.md']
paper_nav_title = 'Papers'

# Get all markdown files in docs/, excluding the ones you don't want under Papers
paper_files = [
    f for f in os.listdir(docs_folder)
    if f.endswith('.md') and f not in exclude_files
]

# Sort for consistency (optional)
paper_files.sort()

# Build the Papers section
papers_nav = f"  - {paper_nav_title}:\n"
for file in paper_files:
    title = os.path.splitext(file)[0].replace('_', ' ').title()
    papers_nav += f"      - {title}: {file}\n"

# Print the section (copy-paste this into mkdocs.yml under `nav:`)
print("Paste this under your 'nav:' section in mkdocs.yml:\n")
print("nav:")
print("  - Home: index.md")
print(papers_nav.rstrip())
print("  - About: about.md")