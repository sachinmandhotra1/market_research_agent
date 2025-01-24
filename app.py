import streamlit as st
import os
from dotenv import load_dotenv
from market_research.crew_setup import MarketResearchCrew
from market_research.report_generator import generate_report_file

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
        .main {
            max-width: 1200px;
            padding: 2rem;
        }
        .stMarkdown {
            font-family: 'Arial', sans-serif;
        }
        .report-content h1 {
            color: #1E88E5;
            font-size: 2.5em;
            margin-bottom: 1em;
            scroll-margin-top: 2em;
        }
        .report-content h2 {
            color: #0D47A1;
            font-size: 2em;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
            border-bottom: 2px solid #E3F2FD;
            padding-bottom: 0.3em;
            scroll-margin-top: 2em;
        }
        .report-content h3 {
            color: #1565C0;
            font-size: 1.5em;
            margin-top: 1.2em;
            scroll-margin-top: 2em;
        }
        .report-content p {
            font-size: 1.1em;
            line-height: 1.6;
            margin-bottom: 1em;
        }
        .report-content blockquote {
            border-left: 4px solid #90CAF9;
            padding-left: 1em;
            margin: 1em 0;
            color: #424242;
        }
        .report-content code {
            padding: 0.2em 0.4em;
            background-color: #E3F2FD;
            border-radius: 3px;
        }
        .report-content table {
            width: 100%;
            margin: 1em 0;
            border-collapse: collapse;
        }
        .report-content th, .report-content td {
            padding: 0.75em;
            border: 1px solid #E0E0E0;
        }
        .report-content th {
            background-color: #E3F2FD;
        }
        .nav-section {
            position: sticky;
            top: 2rem;
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .nav-section a {
            display: block;
            padding: 0.3em 0;
            color: #1565C0;
            text-decoration: none;
            transition: color 0.2s;
        }
        .nav-section a:hover {
            color: #0D47A1;
            text-decoration: underline;
        }
        .download-button {
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background-color: #1E88E5;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .download-button:hover {
            background-color: #1565C0;
        }
        .reset-button {
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background-color: #757575;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .reset-button:hover {
            background-color: #616161;
        }
        </style>
    """, unsafe_allow_html=True)

def create_section_id(header):
    """Create a valid HTML ID from a header"""
    return header.lower().replace(' ', '-').replace(':', '').replace('(', '').replace(')', '')

def process_markdown(content):
    """Process markdown content to render properly"""
    lines = content.split('\n')
    processed_lines = []
    
    for line in lines:
        if line.strip().startswith('#'):
            # Count the number of #s to determine heading level
            level = len(line) - len(line.lstrip('#'))
            text = line.strip('#').strip()
            processed_lines.append(f'<h{level}>{text}</h{level}>')
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def main():
    setup_page_config()
    apply_custom_css()
    
    st.title("Market Research Report Generator")
    
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False
        st.session_state.report_content = None
        st.session_state.report_path = None
    
    if not st.session_state.report_generated:
        st.write("""Enter your research query about a company. You can include:
        - Company name
        - Industry or domain
        - Specific aspects you're interested in
        
        Example queries:
        - "Overview of Delfi Diagnostics Early Cancer Detection"
        - "Market analysis of Tesla in electric vehicles"
        - "Moderna's COVID vaccine development and market position"
        """)

        # Input form
        with st.form("search_form"):
            search_query = st.text_area(
                "Enter your research query",
                height=100,
                help="Enter a natural language query about the company you want to research."
            )
            submit_button = st.form_submit_button("Generate Report")

        if submit_button and search_query:
            try:
                with st.spinner("Gathering information and generating report..."):
                    # Initialize and run the CrewAI workflow
                    crew = MarketResearchCrew()
                    research_data = crew.run_research(search_query)
                    
                    # Generate the report
                    report_path, report_content = generate_report_file(research_data)
                    
                    # Store in session state
                    st.session_state.report_generated = True
                    st.session_state.report_content = report_content
                    st.session_state.report_path = report_path
                    
                    # Rerun to show the report view
                    st.rerun()
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please check if you have set up the required API keys in the .env file.")
    
    else:
        # Report view
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown('<div class="report-content">', unsafe_allow_html=True)
            st.markdown(process_markdown(st.session_state.report_content), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download button below the report
            with open(st.session_state.report_path, "rb") as file:
                filename = os.path.basename(st.session_state.report_path)
                st.download_button(
                    label="📥 Download Report (DOCX)",
                    data=file,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=False
                )
        
        with col2:
            st.markdown('<div class="nav-section">', unsafe_allow_html=True)
            st.markdown("### Quick Navigation")
            # Extract headers and create navigation links
            headers = [line.strip('#').strip() for line in st.session_state.report_content.split('\n') 
                      if line.strip().startswith('#')]
            for header in headers:
                section_id = create_section_id(header)
                st.markdown(
                    f'<a href="#{section_id}" onclick="scrollToSection(\'{section_id}\')">{header}</a>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset button
        if st.button("Generate New Report", key="reset", type="primary"):
            st.session_state.report_generated = False
            st.session_state.report_content = None
            st.session_state.report_path = None
            st.rerun()

if __name__ == "__main__":
    main() 