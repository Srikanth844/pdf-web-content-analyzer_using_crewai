import os
from crewai import Agent, Task, Crew
from typing import Union
import pandas as pd
import fitz
import xml.etree.ElementTree as ET
import requests


# Define Agents
file_reader_agent = Agent(
    role='File Reader',
    goal='Read and extract raw content from various file formats',
    backstory='Expert in parsing different file types with 10 years of experience in data processing',
    verbose=True
)

data_processor_agent = Agent(
    role='Data Processor',
    goal='Process and structure extracted data',
    backstory='Data scientist with deep expertise in transforming raw data into usable formats',
    verbose=True
)

file_writer_agent = Agent(
    role='File Writer',
    goal='Write processed data to text file',
    backstory='Specialist in file operations and data storage',
    verbose=True
)

# Helper Functions
def read_file(input_source: Union[str, bytes]) -> str:
    """Read content from different input sources"""
    try:
        # Handle URL
        if input_source.startswith('http'):
            response = requests.get(input_source)
            # soup = BeautifulSoup(response.content, 'html.parser')
            # return soup.get_text()

        # Handle file paths
        file_extension = os.path.splitext(input_source)[1].lower()
        
        if file_extension == '.pdf':
            text = ""
            with fitz.open(input_source) as pdf:  # Open the PDF file
                for page in pdf:  # Iterate over each page
                    text += page.get_text("text") + "\n"  # Extract text correctly
            return text
                
        elif file_extension == '.csv':
            df = pd.read_csv(input_source)
            return df.to_string()
            
        elif file_extension == '.xlsx':
            tree = ET.parse(input_source)
            root = tree.getroot()
            return ET.tostring(root, encoding='unicode')
            
        else:
            raise ValueError("Unsupported file format")
            
    except Exception as e:
        return f"Error reading input: {str(e)}"

def process_data(raw_content: str) -> str:
    """Process raw content into structured format"""
    try:
        # Basic cleaning and formatting
        processed = raw_content.strip()
        processed = '\n'.join(line for line in processed.splitlines() if line.strip())
        return processed
    except Exception as e:
        return f"Error processing data: {str(e)}"

def write_to_file(content: str, output_path: str = "output.txt") -> str:
    """Write content to text file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return f"Successfully wrote data to {output_path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

# Define Tasks
read_task = Task(
    description='Read and extract content from the input source: {input_source}',
    agent=file_reader_agent,
    expected_output='Raw text content extracted from the input',
    tools=[read_file]
)

process_task = Task(
    description='Process the extracted content into a structured format',
    agent=data_processor_agent,
    expected_output='Cleaned and structured text data',
    tools=[process_data]
)

write_task = Task(
    description='Write the processed data to a text file',
    agent=file_writer_agent,
    expected_output='Confirmation message of successful file write',
    tools=[write_to_file]
)

# Main Application Class
class DataScraperApp:
    def _init_(self):
        self.crew = Crew(
            agents=[file_reader_agent, data_processor_agent, file_writer_agent],
            tasks=[read_task, process_task, write_task],
            verbose=2
        )
    
    def process_input(self, input_source: str) -> dict:
        # Update task descriptions with actual input
        read_task.description = f'Read and extract content from the input source: {input_source}'
        
        # Execute the crew
        result = self.crew.kickoff(inputs={'input_source': input_source})
        return {
            'status': 'success',
            'result': result
        }

# Usage Example
def main():
    # Initialize the app
    app = DataScraperApp()
    
    # Example inputs (uncomment one to test)
    input_source = "example.pdf"
    # input_source = "example.csv"
    # input_source = "example.xml"
    # input_source = "https://example.com"
    
    try:
        result = app.process_input(input_source)
        print(f"Processing completed: {result['result']}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    
    main()
