import os

# Folder where PDFs are located
pdf_folder = 'docs/papers'

# Output folder for the markdown files (same level as index.md)
output_folder = 'docs'

# List all PDF files in the papers folder
pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]

# Loop through PDFs and generate markdown files in docs/
for pdf_file in pdf_files:
    # Generate a clean filename for the .md file
    base_name = os.path.splitext(pdf_file)[0]
    md_filename = f"{base_name}.md"
    md_path = os.path.join(output_folder, md_filename)

    # Create a title from the filename (you can make this prettier if needed)
    title = base_name.replace('_', ' ').title()

    # Markdown content
    content = f"""# {title}

**Authors**: [Author names here]  
**Published**: [Year here]

## Abstract

[Abstract here]

## Paper PDF

[Download the paper](papers/{pdf_file})
"""

    # Write to file
    with open(md_path, 'w') as f:
        f.write(content)

    print(f"Created: {md_path}")