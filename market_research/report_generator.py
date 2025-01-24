import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re


def extract_company_name(content):
    """Extract company name from the report content"""
    # Try to find company name in the first few lines
    first_lines = content.split('\n')[:10]
    for line in first_lines:
        # Look for company name in headers or first paragraph
        if any(word in line.lower() for word in ['overview', 'analysis', 'report']):
            # Extract potential company name
            words = line.strip('#').strip().split()
            for i, word in enumerate(words):
                if word.lower() in ['of', 'for', 'about']:
                    return ' '.join(words[i+1:i+3])  # Take next 2 words after 'of/for/about'
    
    # Fallback to first meaningful words
    for line in first_lines:
        if line.strip() and not line.startswith('#'):
            words = line.strip().split()
            return ' '.join(words[:2])  # Take first two words
    
    return "Company"  # Default fallback

def sanitize_filename(filename):
    """Sanitize the filename to be safe for all operating systems"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove multiple spaces
    filename = ' '.join(filename.split())
    return filename.strip()

def generate_report_file(research_data):
    """
    Generate a formatted Word document from the research data
    """
    doc = Document()
    
    # Document styling
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    
    # Title
    title = doc.add_heading('Market Research Report', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Convert CrewAI output to string if it's not already
    content = str(research_data)
    
    # Split content into sections based on markdown headers
    sections = []
    current_section = []
    
    for line in content.split('\n'):
        if line.strip().startswith('#'):
            if current_section:
                sections.append('\n'.join(current_section))
                current_section = []
        current_section.append(line.strip())
    
    if current_section:
        sections.append('\n'.join(current_section))
    
    # Process each section
    for section in sections:
        if section.strip():
            lines = section.split('\n')
            for line in lines:
                if line.strip().startswith('#'):
                    # Count the number of #s to determine heading level
                    level = min(line.count('#'), 9)
                    text = line.replace('#', '').strip()
                    doc.add_heading(text, level)
                else:
                    if line.strip():
                        doc.add_paragraph(line.strip())
    
    # Save the document
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # Extract company name and create filename
    company_name = extract_company_name(content)
    filename = sanitize_filename(f"Market Analysis of {company_name}.docx")
    report_path = os.path.join('reports', filename)
    
    doc.save(report_path)
    
    return report_path, content 