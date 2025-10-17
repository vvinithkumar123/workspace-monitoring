from markdown2 import markdown
from weasyprint import HTML
import re
import os

def convert_markdown_to_pdf(markdown_file, pdf_file):
    """
    Convert a Markdown file to PDF with a navigable table of contents.
    
    Args:
        markdown_file: Path to the input markdown file
        pdf_file: Path to the output PDF file
    """
    # Read the Markdown content from the file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Extract headings for table of contents
    headings = []
    for line in markdown_content.split('\n'):
        if line.strip().startswith('#'):
            # Extract heading level and text
            match = re.match(r'^(#+)\s+(.+)$', line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2)
                # Create an ID from the heading text
                heading_id = re.sub(r'[^\w\s-]', '', text.lower())
                heading_id = re.sub(r'[-\s]+', '-', heading_id).strip('-')
                headings.append((level, text, heading_id))
    
    # Convert Markdown to HTML with extras for better formatting
    html_body = markdown(markdown_content, extras=['fenced-code-blocks', 'tables', 'header-ids'])
    
    # Build table of contents HTML
    toc_html = '<div class="table-of-contents">\n<h1>Table of Contents</h1>\n<ul>\n'
    for level, text, heading_id in headings:
        indent = '  ' * (level - 1)
        toc_html += f'{indent}<li><a href="#{heading_id}">{text}</a></li>\n'
    toc_html += '</ul>\n</div>\n<div style="page-break-after: always;"></div>\n'
    
    # Create complete HTML document with CSS styling
    html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }}
        
        h3 {{
            color: #555;
            margin-top: 20px;
        }}
        
        .table-of-contents {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        
        .table-of-contents h1 {{
            margin-top: 0;
        }}
        
        .table-of-contents ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .table-of-contents li {{
            margin: 5px 0;
            padding-left: 20px;
        }}
        
        .table-of-contents a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        .table-of-contents a:hover {{
            text-decoration: underline;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        
        table th, table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        
        table th {{
            background-color: #3498db;
            color: white;
        }}
        
        table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #bdc3c7;
            margin: 30px 0;
        }}
        
        a {{
            color: #3498db;
        }}
    </style>
</head>
<body>
    {toc_html}
    {html_body}
</body>
</html>
    '''
    
    # Convert HTML to PDF
    HTML(string=html_content).write_pdf(pdf_file)
    print(f"PDF successfully created: {pdf_file}")

if __name__ == "__main__":
    readme_file = 'readme.md'
    output_pdf_file = 'output.pdf'
    
    if not os.path.exists(readme_file):
        print(f"Error: {readme_file} not found!")
    else:
        convert_markdown_to_pdf(readme_file, output_pdf_file)
