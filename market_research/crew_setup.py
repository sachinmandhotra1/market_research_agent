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
            goal='Analyze gathered information and generate comprehensive insights',
            backstory="""You are a seasoned business analyst with expertise in synthesizing 
            information and generating actionable insights. You excel at identifying key 
            trends, challenges, and opportunities.""",
            verbose=True
        )

        return researcher, scraper, analyst

    def create_tasks(self, researcher, scraper, analyst, search_query):
        # Task 1: Search for relevant articles
        search_task = Task(
            description=f"""Search for comprehensive articles and reliable sources about {search_query}.
            Focus on recent articles from reputable business and industry sources.
            Identify at least 5-7 high-quality sources.""",
            agent=researcher,
            expected_output="""A list of relevant articles with their URLs and brief descriptions,
            focusing on company information, market position, and industry analysis."""
        )

        # Task 2: Scrape and process content
        scrape_task = Task(
            description="""Extract clean, formatted content from the provided URLs using Firecrawl.
            Focus on relevant sections about company overview, products, market position,
            financial data, and future outlook. Ensure the content is concise and relevant.""",
            agent=scraper,
            expected_output="""Clean, structured markdown content from each source, organized by
            key topics including company overview, products, market analysis, and financials.
            Content should be free of HTML and unnecessary elements.""",
            dependencies=[search_task]
        )

        # Task 3: Generate insights report
        analysis_task = Task(
            description="""Analyze the scraped content and generate a comprehensive market research report.
            The report should include:
            1. Introduction
            2. Company overview
            3. Product analysis
            4. Market position and competitive analysis
            5. Regulatory and approval status
            6. Target market and customer segmentation
            7. Financial performance
            8. Challenges and future outlook
            9. Conclusion
            10. Sources""",
            agent=analyst,
            expected_output="""A comprehensive market research report in markdown format,
            covering all required sections with detailed analysis and insights.""",
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