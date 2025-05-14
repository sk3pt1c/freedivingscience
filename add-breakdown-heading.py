import os
import re

folder = 'docs'
excluded_files = {'index.md', 'tags.md'}

for filename in os.listdir(folder):
    if not filename.endswith('.md') or filename in excluded_files:
        continue

    filepath = os.path.join(folder, filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Abstract and Break Down content
    abstract_match = re.search(r'##\s*Abstract\s*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL)
    breakdown_match = re.search(r'##\s*(🧠\s*)?Break Down\s*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL)

    abstract_content = abstract_match.group(1).strip() if abstract_match else ''
    breakdown_content = breakdown_match.group(2).strip() if breakdown_match else ''

    # Remove original abstract and breakdown sections
    if abstract_match:
        content = content.replace(abstract_match.group(0), '')
    if breakdown_match:
        content = content.replace(breakdown_match.group(0), '')

    # Ensure author and published have icons
    content = re.sub(r'\*\*Authors\*\*:', '**👤 Authors**:', content)
    content = re.sub(r'\*\*Published\*\*:', '**📅 Published**:', content)

    # Split content into lines
    lines = content.strip().splitlines()

    # Find index after metadata (after both authors and published lines)
    metadata_end = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("**📅 Published**:"):
            metadata_end = i + 1
            break

    # Build new sections
    insert_lines = []
    if abstract_content:
        insert_lines += ['\n## 🧬 Abstract\n', abstract_content]
    if breakdown_content:
        insert_lines += ['\n## 🧠 Break Down\n', breakdown_content]

    # Insert new sections after metadata
    updated_lines = lines[:metadata_end] + [''] + insert_lines + [''] + lines[metadata_end:]

    updated_content = '\n'.join(updated_lines)

    # Replace Paper PDF heading
    updated_content = re.sub(r'##\s*Paper PDF', '## 📄 Paper PDF', updated_content)

    # Ensure only one 📥 in front of download link
    updated_content = re.sub(r'📥\s*', '', updated_content)  # remove existing icon
    updated_content = re.sub(r'\[Download the paper\]', '📥 [Download the paper]', updated_content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"✅ Updated: {filename}")