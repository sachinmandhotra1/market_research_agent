from crewai import Agent, Task, Crew
from crewai_tools import SerpApiGoogleSearchTool, FirecrawlScrapeWebsiteTool
import os

class MarketResearchCrew:
    def __init__(self):
        self.setup_tools()

    def setup_tools(self):
        # Setup Google Search Tool using built-in CrewAI tool
        self.search_tool = SerpApiGoogleSearchTool()

        # Setup Firecrawl Web Scraping Tool
        self.scrape_tool = FirecrawlScrapeWebsiteTool(
            api_key=os.getenv("FIRECRAWL_API_KEY"),
            page_options={
                "onlyMainContent": True,
                "timeout": 30000,
                "waitFor": 2000
            }
        )

    def create_agents(self):
        # Research Agent
        researcher = Agent(
            role='Market Research Analyst',
            goal='Find relevant and high-quality articles about the company and its market',
            backstory="""You are an experienced market research analyst with expertise in 
            finding and analyzing company and industry information. Your strength lies in 
            identifying reliable sources and relevant content.""",
            tools=[self.search_tool],
            verbose=True
        )

        # Content Scraper Agent
        scraper = Agent(
            role='Content Scraper',
            goal='Extract and process content from identified sources',
            backstory="""You are a specialist in web scraping and content processing. 
            You know how to extract relevant information and format it properly using Firecrawl.
            You focus on getting clean, relevant content without HTML or unnecessary elements.""",
            tools=[self.scrape_tool],
            verbose=True
        )

        # Analysis Agent
        analyst = Agent(
            role='Business Analyst',
            goal='Analyze gathered information and generate comprehensive insights with proper citations',
            backstory="""You are a seasoned business analyst with expertise in synthesizing 
            information and generating actionable insights. You excel at identifying key 
            trends, challenges, and opportunities. You are meticulous about citing sources 
            and providing proper attribution for all information. You ensure that every 
            significant claim or data point is backed by a source URL.""",
            verbose=True
        )

        return researcher, scraper, analyst

    def create_tasks(self, researcher, scraper, analyst, search_query):
        # Task 1: Search for relevant articles
        search_task = Task(
            description=f"""Search for comprehensive articles and reliable sources about {search_query}.
            Focus on recent articles from reputable business and industry sources.
            
            Required source types (minimum 2-3 from each):
            1. Market Research Reports
               - Industry analysis reports
               - Market size and forecasts
               - Competitive landscape studies
            
            2. Scientific Publications
               - Peer-reviewed journals
               - Research papers
               - Clinical studies
            
            3. Industry News & Analysis
               - Business news articles
               - Industry expert opinions
               - Market trends coverage
            
            4. Company Resources
               - Official company materials
               - Press releases
               - Executive interviews
            
            5. Regulatory & Government
               - Regulatory guidelines
               - Government reports
               - Policy documents
            
            6. Healthcare Organizations
               - Medical associations
               - Healthcare institutions
               - Clinical guidelines
            
            Ensure sources are:
            - Recent (preferably within last 2 years)
            - Authoritative and reliable
            - Diverse across categories
            - Relevant to the specific query
            
            Identify at least 12-15 high-quality sources total.""",
            agent=researcher,
            expected_output="""A comprehensive list of relevant articles with their URLs and brief descriptions,
            organized by category and focusing on company information, market position, and industry analysis."""
        )

        # Task 2: Scrape and process content
        scrape_task = Task(
            description="""Extract clean, formatted content from the provided URLs using Firecrawl.
            Focus on relevant sections about company overview, products, market position,
            financial data, and future outlook. 
            
            For each source:
            1. Extract key data points and statistics
            2. Identify relevant quotes and insights
            3. Note publication date and author/organization
            4. Capture methodology and data sources
            
            Format requirements:
            - Clean, structured content
            - Remove HTML and unnecessary elements
            - Preserve important formatting
            - Maintain source attribution""",
            agent=scraper,
            expected_output="""Clean, structured markdown content from each source, organized by
            key topics with proper attribution and formatting.""",
            dependencies=[search_task]
        )

        # Task 3: Generate insights report
        analysis_task = Task(
            description="""Analyze the scraped content and generate a comprehensive market research report.
            
            Citation format:
            - Use inline citations: "Text [Source Name](URL)"
            - Example: "According to [Nature Medicine](URL), the technology..."
            - Never show raw URLs in the text
            - Include all sources in the appendix
            
            Report structure:
            1. Executive Summary
               - Brief overview of key findings
               - Market highlights
               - Strategic recommendations
            
            2. Company Overview
               - Company history and background
               - Mission and vision
               - Key leadership and organizational structure
            
            3. Product/Service Analysis
               - Core offerings
               - Key features and benefits
               - Technology and innovation
               - Product development pipeline
            
            4. Market Analysis
               - Industry overview and size
               - Market trends and dynamics
               - Growth drivers and barriers
               - Competitive landscape
            
            5. Business Strategy
               - Go-to-market strategy
               - Revenue model
               - Strategic partnerships
               - Geographic presence
            
            6. Financial Analysis
               - Revenue and growth metrics
               - Funding and investments
               - Key financial indicators
               - Future projections
            
            7. SWOT Analysis
               - Strengths
               - Weaknesses
               - Opportunities
               - Threats
            
            8. Future Outlook
               - Growth opportunities
               - Potential challenges
               - Industry predictions
               - Strategic recommendations
            
            9. Conclusion
               - Key takeaways
               - Strategic implications
               - Final recommendations
            
            10. Appendix: Sources and Citations
                - List all sources with URLs
                - Date of access for each source
                - Additional reference materials
            
            Formatting requirements:
            1. Use proper markdown formatting
            2. Each point should be on a new line
            3. Use bullet points for lists
            4. Use proper hierarchy for sections
            5. Keep paragraphs concise
            6. Include source citations for all claims
            
            Sources section format:
            - Group sources by category
            - Include full source name and link
            - Remove access dates
            - Sort by relevance within categories""",
            agent=analyst,
            expected_output="""A comprehensive market research report in markdown format,
            with proper formatting, citations, and clear structure.""",
            dependencies=[scrape_task]
        )

        return [search_task, scrape_task, analysis_task]

    def run_research(self, search_query):
        # Create agents
        researcher, scraper, analyst = self.create_agents()
        
        # Create tasks
        tasks = self.create_tasks(researcher, scraper, analyst, search_query)
        
        # Create and run the crew
        crew = Crew(
            agents=[researcher, scraper, analyst],
            tasks=tasks,
            verbose=True
        )
        
        result = crew.kickoff()
        return result 