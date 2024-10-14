# Import necessary libraries for web scraping and HTML parsing
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup  # HTML parser

# Function that takes a website URL and returns its HTML content
def scrape_website(website):
    print("Launching chrome browser...")  # Log the browser launch
    
    # Path to the ChromeDriver executable
    chrome_driver_path = "./chromedriver.exe"
    
    # Set Chrome options (default, can be customized later if needed)
    options = webdriver.ChromeOptions()
    
    # Initialize the Chrome WebDriver using the specified ChromeDriver path and options
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

    try:
        # Navigate to the website URL using the Chrome driver
        driver.get(website)
        print("Page loaded...")  # Log when the page is loaded successfully
        
        # Get the HTML source of the loaded page
        html = driver.page_source
        
        # Return the HTML content of the webpage
        return html
    finally:
        # Ensure that the browser is closed even if an error occurs
        driver.quit()

# Function to extract only the <body> content from the raw HTML
def extract_body_content(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Find the <body> tag and extract its content
    body_content = soup.body
    
    # If the <body> content exists, return it as a string; otherwise return an empty string
    if body_content:
        return str(body_content)
    return ""

# Function to clean the extracted <body> content by removing <script> and <style> tags
def clean_body_content(body_content):
    # Parse the body content using BeautifulSoup
    soup = BeautifulSoup(body_content, "html.parser")

    # Remove all <script> and <style> tags, as they are not needed for the LLM
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()  # Extract and remove these tags

    # Get all the remaining text in the body, separating each element by a newline
    cleaned_content = soup.get_text(separator="\n")

    # Strip extra whitespace and remove empty lines, keeping only meaningful text
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    # Return the cleaned content, now free of scripts and styles
    return cleaned_content

# Function to split the cleaned content into chunks, respecting LLM input size limits
def split_dom_content(dom_content, max_length=6000):
    # Split the content into smaller chunks based on the maximum allowed length (e.g., 6000 characters)
    return [
        dom_content[i: i + max_length]  # Get the substring from i to i+max_length
        for i in range(0, len(dom_content), max_length)  # Iterate over the content in steps of max_length
    ]
