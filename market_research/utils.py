import streamlit as st
import re


def setup_page_config():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title="Market Research Report Generator",
        page_icon="📊",
        layout="wide"
    )

def apply_custom_css():
    """Apply custom CSS for better markdown rendering"""
    st.markdown("""
        <style>
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        /* Top Navigation Bar */
        .nav-bar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: white;
            padding: 0 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #e0e0e0;
            z-index: 1000;
        }

        .back-button {
            display: flex;
            align-items: center;
            color: #333;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
        }

        .download-button {
            background: #2E7D32;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
        }

        /* Main Layout */
        .report-container {
            display: flex;
            margin-top: 60px;
            height: calc(100vh - 60px);
        }

        /* Sidebar Navigation */
        .sidebar {
            width: 280px;
            background: #f8f9fa;
            border-right: 1px solid #e0e0e0;
            padding: 24px;
            height: 100%;
            overflow-y: auto;
            flex-shrink: 0;
        }

        .sidebar h3 {
            color: #333;
            font-size: 16px;
            margin-bottom: 16px;
            font-weight: 600;
        }

        .nav-links {
            list-style: none;
        }

        .nav-item {
            display: block;
            padding: 8px 0;
            color: #666;
            text-decoration: none;
            font-size: 14px;
            transition: color 0.2s;
        }

        .nav-item:hover {
            color: #2E7D32;
        }

        /* Main Content */
        .content {
            flex: 1;
            padding: 32px 48px;
            overflow-y: auto;
        }

        /* Typography */
        h1 {
            font-size: 24px;
            color: #333;
            margin-bottom: 24px;
        }

        h2 {
            font-size: 20px;
            color: #333;
            margin: 32px 0 16px;
        }

        h3 {
            font-size: 18px;
            color: #333;
            margin: 24px 0 12px;
        }

        p {
            font-size: 16px;
            color: #444;
            line-height: 1.6;
            margin-bottom: 16px;
        }

        /* Lists */
        ul {
            margin: 16px 0;
            padding-left: 24px;
        }

        li {
            font-size: 16px;
            color: #444;
            line-height: 1.6;
            margin-bottom: 12px;
        }

        /* Source Links */
        .source-link {
            color: #2E7D32;
            text-decoration: none;
            font-weight: 500;
        }

        .source-link:hover {
            text-decoration: underline;
        }

        /* Sources Section */
        .sources-section {
            margin-top: 40px;
            border-top: 1px solid #e0e0e0;
            padding-top: 24px;
        }

        .source-category {
            margin-bottom: 24px;
        }

        .source-category h3 {
            color: #333;
            font-size: 18px;
            margin-bottom: 16px;
        }

        .source-item {
            margin-bottom: 12px;
            line-height: 1.6;
        }

        .source-title {
            font-weight: 500;
            color: #333;
            margin-right: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

def create_section_id(header, index=None):
    """Create a valid HTML ID from a header, including index if provided"""
    base_id = re.sub(r'[^a-z0-9-]', '', header.lower().replace(' ', '-'))
    return f"{index}-{base_id}" if index is not None else base_id

def process_markdown(content):
    """Process markdown content with better formatting"""
    lines = content.split('\n')
    processed_lines = []
    in_list = False
    current_section = None
    
    for line in lines:
        if line.strip().startswith('#'):
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            level = len(line) - len(line.lstrip('#'))
            text = line.strip('#').strip()
            section_id = create_section_id(text)
            processed_lines.append(f'<div id="{section_id}" class="section-header level-{level}">')
            processed_lines.append(f'<h{level}>{text}</h{level}>')
            processed_lines.append('</div>')
            current_section = text
        elif line.strip().startswith('**'):
            # Handle bold headers within sections
            text = line.strip('*').strip()
            processed_lines.append(f'<h3 class="subsection-header">{text}</h3>')
        elif line.strip().startswith('- '):
            if not in_list:
                processed_lines.append('<ul class="content-list">')
                in_list = True
            text = line.strip('- ').strip()
            if 'source:' in text.lower():
                # Format source links
                text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" class="source-link">\1</a>', text)
            processed_lines.append(f'<li>{text}</li>')
        elif line.strip():
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            processed_lines.append(f'<p>{line}</p>')
        else:
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            processed_lines.append('<br>')
    
    if in_list:
        processed_lines.append('</ul>')
    
    return '\n'.join(processed_lines)

def format_sources_section(content):
    """Format the sources section"""
    sources = []
    current_category = None
    
    for line in content.split('\n'):
        if line.strip().startswith('- '):
            match = re.match(r'- (.*?) - \[(.*?)\]\((.*?)\)', line.strip())
            if match:
                title, text, url = match.groups()
                sources.append({
                    'title': title,
                    'text': text,
                    'url': url,
                    'category': current_category
                })
    
    # Group sources by category
    categories = {}
    for source in sources:
        cat = source['category'] or 'Other Sources'
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(source)
    
    # Generate HTML
    html = ['<div class="sources-section">']
    for category, items in categories.items():
        html.append(f'<div class="source-category">')
        html.append(f'<h3>{category}</h3>')
        for item in items:
            html.append(
                f'<div class="source-item">'
                f'<span class="source-title">{item["title"]}</span>'
                f'<a href="{item["url"]}" class="source-link">{item["text"]}</a>'
                f'</div>'
            )
        html.append('</div>')
    html.append('</div>')
    
    return '\n'.join(html)
