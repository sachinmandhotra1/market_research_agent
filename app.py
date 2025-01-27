import streamlit as st
import os
from dotenv import load_dotenv
from market_research.crew_setup import MarketResearchCrew
from market_research.report_generator import generate_report_file
import re

# Load environment variables
load_dotenv()

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

def create_section_id(header):
    """Create a valid HTML ID from a header"""
    return re.sub(r'[^a-z0-9-]', '', header.lower().replace(' ', '-'))

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

def main():
    setup_page_config()
    
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False
        st.session_state.report_content = None
        st.session_state.report_path = None
    
    if not st.session_state.report_generated:
        st.title("Market Research Report Generator")
        
        # Main input with help tooltip
        col1, col2 = st.columns([10, 1])
        with col1:
            st.write("Enter your research query about a company.")
        with col2:
            st.markdown("""
                <style>
                .tooltip {
                    position: relative;
                    display: inline-block;
                }
                .tooltip .tooltiptext {
                    visibility: hidden;
                    width: 300px;
                    background-color: #f8f9fa;
                    color: #333;
                    text-align: left;
                    border-radius: 6px;
                    padding: 12px;
                    position: absolute;
                    z-index: 1;
                    right: 105%;
                    top: -10px;
                    opacity: 0;
                    transition: opacity 0.3s;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border: 1px solid #e0e0e0;
                }
                .tooltip:hover .tooltiptext {
                    visibility: visible;
                    opacity: 1;
                }
                .help-icon {
                    color: #666;
                    cursor: help;
                }
                </style>
                <div class="tooltip">
                    <span class="help-icon">❔</span>
                    <span class="tooltiptext">
                        <strong>You can include:</strong><br>
                        • Company name<br>
                        • Industry or domain<br>
                        • Specific aspects you're interested in<br><br>
                        <strong>Sample queries:</strong><br>
                        • "Overview of Delfi Diagnostics Early Cancer Detection"<br>
                        • "Market analysis of Tesla in electric vehicles"<br>
                        • "Moderna's COVID vaccine development and market position"
                    </span>
                </div>
            """, unsafe_allow_html=True)

        # Input form
        with st.form("search_form"):
            search_query = st.text_area(
                "Enter your research query",
                height=100
            )
            submit_button = st.form_submit_button("Generate Report")

        if submit_button and search_query:
            try:
                with st.spinner("Gathering information and generating report..."):
                    crew = MarketResearchCrew()
                    research_data = crew.run_research(search_query)
                    report_path, report_content = generate_report_file(research_data)
                    st.session_state.report_generated = True
                    st.session_state.report_content = report_content
                    st.session_state.report_path = report_path
                    st.session_state.search_query = search_query  # Store search query
                    st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        # Navigation bar
        col1, col2 = st.columns([6, 1])
        with col1:
            if st.button("← Back to research page", key="back_button"):
                st.session_state.report_generated = False
                st.rerun()
        with col2:
            if st.session_state.report_path:
                query = st.session_state.get('search_query', '')
                company_name = ' '.join(word.capitalize() for word in query.split()[:4])
                download_filename = f"Market Research Report of {company_name}.docx"
                
                with open(st.session_state.report_path, "rb") as file:
                    st.download_button(
                        "Download Report",
                        data=file,
                        file_name=download_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_button"
                    )
        
        # Main layout
        col1, col2 = st.columns([1, 4])
        
        # Quick links in left column
        with col1:
            sections = []
            # Extract main sections only (level 2 headers)
            for line in st.session_state.report_content.split('\n'):
                if line.strip().startswith('## '):
                    text = line.strip('#').strip()
                    # Remove any numbering
                    text = re.sub(r'^\d+\.\s*', '', text)
                    # Skip title and report name
                    if not text.lower().startswith(('comprehensive', 'market research', 'generated')):
                        sections.append(text)
            
            # Display sections as simple clickable text links
            for section in sections:
                section_id = create_section_id(section)
                st.markdown(
                    f'<a href="#{section_id}" '
                    f'style="color: #333; text-decoration: none; display: block; padding: 5px 0; '
                    f'transition: color 0.2s;" '
                    f'onmouseover="this.style.color=\'#2E7D32\'" '
                    f'onmouseout="this.style.color=\'#333\'">'
                    f'{section}'
                    f'</a>',
                    unsafe_allow_html=True
                )
                    
        # Main content
        with col2:
            if st.session_state.report_content:
                st.title("Generated Report")
                
                # Split content into lines
                lines = st.session_state.report_content.split('\n')
                
                # Get report name
                report_name = next((line.strip('#').strip() for line in lines if line.strip().startswith('# ')), "")
                if report_name:
                    # Extract company/entity name from search query
                    query = st.session_state.get('search_query', '')
                    company_name = ' '.join(word.capitalize() for word in query.split()[:4])
                    st.markdown(f"### Market Research Report: {company_name}")
                
                # Process content
                current_section = []
                for line in lines[1:]:
                    if line.strip().startswith('#'):
                        if current_section:
                            content = '\n'.join(current_section)
                            
                            # Remove section numbering
                            content = re.sub(r'^\d+\.\s*', '', content, flags=re.MULTILINE)
                            
                            # Format section headers
                            if "Sources" in content or "Appendix" in content:
                                # Process sources
                                st.markdown("## Sources")
                                current_category = None
                                for source_line in content.split('\n'):
                                    if source_line.strip():
                                        if source_line.startswith('###'):
                                            # Category header without numbering
                                            current_category = source_line.strip('#').strip()
                                            # Remove any numbering from category
                                            current_category = re.sub(r'^\d+\.\s*', '', current_category)
                                            st.markdown(f"### {current_category}")
                                        elif '[' in source_line and ']' in source_line:
                                            # Extract title and URL, ensure proper bullet point format
                                            match = re.match(r'\[(.*?)\]\((.*?)\)', source_line)
                                            if match:
                                                title, url = match.groups()
                                                st.markdown(f"- [{title}]({url})")
                            else:
                                # Format regular content
                                paragraphs = content.split('\n\n')
                                for para in paragraphs:
                                    if para.strip():
                                        st.markdown(para)
                                
                            st.markdown("---")
                            current_section = []
                    current_section.append(line)
                
                if current_section:
                    content = '\n'.join(current_section)
                    st.markdown(content)
                    st.markdown("---")

if __name__ == "__main__":
    main() 