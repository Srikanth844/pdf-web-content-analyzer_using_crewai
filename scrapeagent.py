from crewai import Agent, Task, Crew
from playwright.sync_api import sync_playwright
import pandas as pd
import fitz
import os

# Define an agent for web scraping
class WebScraper:
    def scrape_url(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            data = page.content()  # Extract HTML content
            browser.close()
        return data

scraper_agent = Agent(
    role="Web Scraper",
    goal="Extract content from given URLs using Playwright.",
    backstory="An expert at fetching and analyzing web data efficiently.",
    allow_delegation=False,
    function_calling_llm=WebScraper.scrape_url  # Correct function reference
)

# Define an agent for PDF extraction
class PDFExtractor:
    def extract_text(self, pdf_path):
        text = ""
        with fitz.open(pdf_path) as pdf:  # Open the PDF file
            for page in pdf:  # Iterate over each page
                text += page.get_text("text") + "\n"  # Extract text correctly
        return text

pdf_agent = Agent(
    role="PDF Processor",
    goal="Extract text from PDFs for data analysis.",
    backstory="Specializes in extracting and summarizing textual data from PDFs.",
    function_calling_llm=PDFExtractor.extract_text  # Correct function reference
)
# Define an agent for CSV processing
class CSVProcessor:
    def process_csv(self, csv_path):
        df = pd.read_csv(csv_path)
        return df.head().to_dict()  # Return first few rows as sample output

csv_agent = Agent(
    role="CSV Processor",
    goal="Process CSV files and extract relevant information.",
    backstory="Expert in handling structured data for analysis.",
    function_calling_llm=CSVProcessor.process_csv  # Correct function reference
)

# Define a Manager agent to coordinate the workflow
manager_agent = Agent(
    role="AI Workflow Manager",
    goal="Coordinate web scraping, PDF extraction, and CSV processing tasks.",
    backstory="Orchestrates multiple AI agents to automate data collection and analysis."
)

# Define tasks
# Define tasks with required 'type' field
task_scrape_web = Task(
    type="scraping_task",  # Add the 'type' field
    description="Scrape the given URL and extract relevant data.",
    expected_output="Extracted HTML content",  # Assuming this field is required
    agent=scraper_agent
)

task_extract_pdf = Task(
    type="pdf_extraction",  # Add the 'type' field
    description="Extract text from a PDF document.",
    expected_output="Extracted text from the PDF",  # Assuming this field is required
    agent=pdf_agent
)

task_process_csv = Task(
    type="csv_processing",  # Add the 'type' field
    description="Process and analyze data from a CSV file.",
    expected_output="Sample rows from CSV",  # Assuming this field is required
    agent=csv_agent
)



# Assemble the Crew
crew = Crew(
    agents=[scraper_agent, pdf_agent, csv_agent, manager_agent],
    tasks=[task_scrape_web, task_extract_pdf, task_process_csv],
    verbose=True
)

# Execute the workflow


# Example Inputs (optional for testing agents individually)
url = "https://playwright.dev/python/docs/librarypython"
# pdf_file = "sample.pdf"
# csv_file = "data.csv"

# Running Agents Individually (for testing)
# web_data=scraper_agent.call(url)
# # pdf_text = pdf_agent.function(pdf_file)
# # csv_data = csv_agent.function(csv_file)

# print("Scraped Web Data:", web_data[:500])  # Print first 500 characters
# print("Extracted PDF Text:", pdf_text[:500])
# print("CSV Data Sample:", csv_data)
crew.kickoff(inputs=url)