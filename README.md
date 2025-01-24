# Market Research Report Generator

A Streamlit application that generates comprehensive market research reports using CrewAI framework.

## Features

- Search for company information using Google Search
- Scrape and analyze relevant web content
- Generate structured market research reports
- Export reports in DOCX format

## Prerequisites

- Python 3.10+
- SerpAPI API key
- Firecrawl API key

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```
SERPAPI_API_KEY="your_serpapi_key_here"
FIRECRAWL_API_KEY="your_firecrawl_key_here"
OPENAI_API_KEY="your_openai_api_key"
OPENAI_MODEL_NAME="your_model_name_here"
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Enter a company name and domain in the search box
3. Click "Generate Report"
4. Wait for the analysis to complete
5. Download the generated report

## Report Structure

The generated report includes:
- Introduction
- Company overview
- Product analysis
- Market position and competitive analysis
- Regulatory and approval status
- Target market and customer segmentation
- Financial performance
- Challenges and future outlook
- Conclusion
- Sources 