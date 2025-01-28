import streamlit as st
import os
from dotenv import load_dotenv
from market_research.crew_setup import MarketResearchCrew, LLM
from market_research.report_generator import generate_report_file, generate_report_title
from market_research.utils import *
import re

# Load environment variables
load_dotenv()


def main(llm_model: LLM):
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
                    crew = MarketResearchCrew(llm_model)
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
                report_title = generate_report_title(query)
                download_filename = f"Market Research Report of {report_title}.docx"
                
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
            for line in st.session_state.report_content.split('\n'):
                if line.strip().startswith('## '):
                    text = line.strip('#').strip()
                    text = re.sub(r'^\d+\.\s*', '', text)
                    if not text.lower().startswith(('comprehensive', 'market research', 'generated')):
                        sections.append(text)
            
            for index, section in enumerate(sections, start=1):
                section_id = create_section_id(section, index)
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
                
                lines = st.session_state.report_content.split('\n')
                
                report_name = next((line.strip('#').strip() for line in lines if line.strip().startswith('# ')), "")
                if report_name:
                    query = st.session_state.get('search_query', '')
                    company_name = ' '.join(word.capitalize() for word in query.split()[:4])
                    report_title = generate_report_title(query)
                    st.markdown(f"### {report_title}")
                else:
                    report_title = company_name
                
                current_section = []
                section_index = 1
                for line in lines[1:]:
                    if line.strip().startswith('#'):
                        if current_section:
                            content = '\n'.join(current_section)
                            content = re.sub(r'^\d+\.\s*', '', content, flags=re.MULTILINE)
                            section_id = create_section_id(current_section[0].strip('#').strip(), section_index)
                            st.markdown(f'<div id="{section_id}"></div>', unsafe_allow_html=True)
                            paragraphs = content.split('\n\n')
                            for para in paragraphs:
                                if para.strip():
                                    st.markdown(para)
                            st.markdown("---")
                            current_section = []
                            section_index += 1
                    current_section.append(line)
                
                if current_section:
                    content = '\n'.join(current_section)
                    section_id = create_section_id(current_section[0].strip('#').strip(), section_index)
                    st.markdown(f'<div id="{section_id}"></div>', unsafe_allow_html=True)
                    st.markdown(content)
                    st.markdown("---")


if __name__ == "__main__":

    # Requires OPENAI_API_KEY in the .env file
    openai_llm = LLM(
        model="gpt-4o-mini",
        temperature=0.1
    )

    # Requires GEMINI_API_KEY in the .env file
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash-exp",
        temperature=0.1
    )

    # Requires ANTHROPIC_API_KEY in the .env file
    anthropic_llm = LLM(
        model="anthropic/claude-3-sonnet-20240229-v1:0",
        temperature=0.1
    )

    llm = openai_llm

    main(llm_model=llm)
