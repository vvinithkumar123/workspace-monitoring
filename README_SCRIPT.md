# Markdown to PDF Converter

This Python script converts Markdown files to PDF format with a navigable table of contents.

## Features

- **Automatic Table of Contents**: Generates a clickable TOC from all headings in the markdown file
- **Navigable Links**: All TOC entries link to their corresponding sections in the PDF
- **Professional Styling**: Clean, readable PDF output with proper formatting
- **Code Block Support**: Properly formatted code blocks and tables
- **Command-line Interface**: Easy to use with flexible input/output options

## Requirements

- Python 3.6+
- markdown2
- weasyprint

## Installation

1. Clone this repository or download the script
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install dependencies manually:

```bash
pip install markdown2 weasyprint
```

## Usage

### Basic Usage

Convert `readme.md` to `output.pdf` (default):

```bash
python3 markdown_to_pdf.py
```

### Custom Input File

Convert a specific markdown file:

```bash
python3 markdown_to_pdf.py document.md
```

### Custom Input and Output Files

Convert a specific markdown file to a specific PDF:

```bash
python3 markdown_to_pdf.py readme.md workspace-guide.pdf
```

### Get Help

Display help information:

```bash
python3 markdown_to_pdf.py --help
```

## Output

The script generates a PDF with:

1. **Table of Contents** - A navigable index of all headings on the first page(s)
2. **Page Break** - Separates TOC from content
3. **Formatted Content** - All markdown content properly formatted including:
   - Headings (H1-H6)
   - Code blocks with syntax highlighting
   - Tables
   - Lists (ordered and unordered)
   - Links
   - Emphasis (bold, italic)
   - Horizontal rules

## Example

Given a markdown file `readme.md`:

```markdown
# My Document

## Introduction

Some introduction text.

## Main Content

### Section 1
Content here.

### Section 2
More content.
```

Running:
```bash
python3 markdown_to_pdf.py readme.md output.pdf
```

Will create a PDF with:
- A clickable table of contents listing all sections
- All headings properly formatted and linkable from the TOC
- Professional styling and layout

## Customization

The script includes built-in CSS styling. To customize the appearance, edit the `<style>` section in the `convert_markdown_to_pdf()` function.

### Available Style Sections

- `body`: Overall document styling
- `h1, h2, h3`: Heading styles
- `.table-of-contents`: TOC styling
- `code, pre`: Code block styling
- `table`: Table styling

## Troubleshooting

### WeasyPrint Installation Issues

WeasyPrint requires some system dependencies. If you encounter issues:

**On Ubuntu/Debian:**
```bash
sudo apt-get install -y python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
```

**On macOS:**
```bash
brew install python3 cairo pango gdk-pixbuf libffi
```

**On Windows:**
Follow the [WeasyPrint documentation](https://weasyprint.readthedocs.io/en/stable/install.html) for Windows-specific instructions.

### Missing Fonts

If certain characters don't render correctly, ensure you have the necessary fonts installed on your system.

## License

This script is provided as-is for use in the workspace-monitoring project.

## Author

Created for the vvinithkumar123/workspace-monitoring repository.
