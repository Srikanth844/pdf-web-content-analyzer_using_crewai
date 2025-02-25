from crewai import Agent, Task, Crew
import fitz  # PyMuPDF
import os
from playwright.sync_api import sync_playwright

def extract_pdf_content(pdf_path):
    """
    Extract text content from a PDF file.
    
    Args:
    pdf_path (str): Path to the PDF file.
    
    Returns:
    str: Extracted text content from the PDF.
    """
    text_content = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text_content += page.get_text()
    except Exception as e:
        print(f"Error extracting PDF content: {e}")
    return text_content

def scrape_url_content(url):
    """
    Scrape content from a given URL using Playwright.
    
    Args:
    url (str): URL to scrape.
    
    Returns:
    str: Scraped content from the URL.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        content = page.content()
        browser.close()
    return content

# Create an agent to process the extracted PDF content
content_processor = Agent(
    role='content Processor',
    goal='Process and analyze text content extracted from PDF files or web pages',
    backstory='You are an expert in analyzing and summarizing textual content from various documents.',
    verbose=True
)

# Create a task to process the PDF content
def create_processing_task(source):
    if source.startswith('http'):
        content = scrape_url_content(source)
        source_type = "web page"
    else:
        content = extract_pdf_content(source)
        source_type = "PDF"
    return Task(
        description=f'Analyze and summarize the following {source_type} content:\n\n{content[:1000]}...',  # Truncated for brevity
        expected_output='Raw text content extracted from the input',
        agent=content_processor
    )

# Create an agent to write content to a text file
file_writer = Agent(
    role='File Writer',
    goal='Write processed content to text files',
    backstory='You are skilled at creating and writing to text files.',
    verbose=True
)

# Create a task to write the processed content to a text file
write_task = Task(
    description='Write the processed ontent to a text file named "output.txt".',
    expected_output='Confirmation message of successful file write',
    agent=file_writer
)

def process_content(source):
    # Create a crew to manage the agents and tasks
    content_crew = Crew(
        agents=[content_processor, file_writer],
        tasks=[create_processing_task(source), write_task],
        verbose=True
    )

    # Execute the tasks
    result = content_crew.kickoff()

    # Write the result to a text file
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write(str(result))

    print("PDF content has been processed and written to output.txt")

if __name__ == "__main__":
    # For PDF
    # process_content('path/to/your/document.pdf')
    
    # For URL
    process_content('https://docs.crewai.com/concepts/tasks')