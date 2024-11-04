import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from bs4 import BeautifulSoup  # HTML parser
import time
import streamlit as st


# Function to initialize the browser driver
def get_browser_driver(browser="chrome"):
    if browser.lower() == "firefox":
        print("Launching Firefox browser...")
        firefox_driver_path = "./geckodriver.exe"
        options = webdriver.FirefoxOptions()
        driver = webdriver.Firefox(service=FirefoxService(firefox_driver_path), options=options)
    else:
        print("Launching Chrome browser...")
        chrome_driver_path = "./chromedriver.exe"
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=ChromeService(chrome_driver_path), options=options)
    return driver

# Function that takes a website URL and returns the HTML content
def scrape_website(website, browser="chrome"):
    driver = get_browser_driver(browser)
    
    try:
        # Navigate to the website URL
        driver.get(website)
        print("Page loaded...")
        time.sleep(3)  # Allow the page to fully load
        
        # Get the HTML source of the loaded page
        html = driver.page_source
        return html
    finally:
        driver.quit()

# Function to scrape all links or associated URLs for transcripts
def scrape_all_links(website, browser="chrome"):
    driver = get_browser_driver(browser)

    try:
        # Go to the website
        driver.get(website)
        print("Page loaded...")
        time.sleep(3)

        # Parse the page with BeautifulSoup to find the relevant elements
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        
        # Find all <span> elements with the class "entry-title p-name"
        titles = soup.find_all("span", class_="entry-title p-name")
        print(f"Found {len(titles)} transcript titles.")

        # Attempt to find links associated with each title
        article_links = []
        base_url = "http://en.kremlin.ru"  # Base URL for constructing full links
        
        for title in titles:
            parent = title.find_parent("a")  # Find the parent <a> tag (link) if it exists
            if parent and 'href' in parent.attrs:
                relative_url = parent['href']  # Get the href attribute (the link)
                # Ensure the URL is properly constructed by removing duplicate path parts
                if not relative_url.startswith("http"):
                    # Correctly format relative links
                    full_url = base_url + relative_url
                else:
                    full_url = relative_url
                
                # Clean up any extra paths or repetitions in the link (e.g., duplicates like "/events/president/transcripts/events/...")
                if "/events/president/transcripts/events" in full_url:
                    full_url = full_url.replace("/events/president/transcripts/events", "/events/president/transcripts")

                article_links.append(full_url)

        print(f"Found {len(article_links)} article links.")
        return article_links
    finally:
        driver.quit()


# Function to scrape content from each individual page, focusing on specific elements
def scrape_individual_page(url, browser="chrome"):
    driver = get_browser_driver(browser)

    try:
        # Load the page
        driver.get(url)
        time.sleep(3)
        html = driver.page_source
        
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Extract the title (h1 element with class "entry-title")
        title_element = soup.find("h1", class_="entry-title p-name")
        title = title_element.get_text(strip=True) if title_element else "No title found"
        st.write(f"Extracted Title: {title}")  # Debugging output

        # Extract the summary (div with class "read__lead entry-summary")
        summary_element = soup.find("div", class_="read__lead entry-summary p-summary")
        summary = summary_element.get_text(strip=True) if summary_element else "No summary found"
        st.write(f"Extracted Summary: {summary}")  # Debugging output

        # Extract the main content (div with class "entry-content")
        content_element = soup.find("div", class_="entry-content e-content read__internal_content")

        # Get all paragraph <p> tags inside this div for the speech content
        paragraphs = content_element.find_all("p") if content_element else []
        content = "\n\n".join(p.get_text(strip=True) for p in paragraphs)
        st.write(f"Extracted Content Length: {len(content)}")  # Debugging output

        # Return the extracted title, summary, and content
        return {
            "title": title,
            "summary": summary,
            "content": content if content else "No content found"
        }
    except Exception as e:
        st.write(f"Error while scraping {url}: {str(e)}")
        return {
            "title": "Error",
            "summary": "Error",
            "content": "Error"
        }
    finally:
        driver.quit()

# Function to scrape all links or associated URLs for transcripts
def scrape_all_links(website, browser="chrome"):
    driver = get_browser_driver(browser)

    try:
        # Go to the website
        driver.get(website)
        print("Page loaded...")
        time.sleep(3)

        # Parse the page with BeautifulSoup to find the relevant elements
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        
        # Find all <span> elements with the class "entry-title p-name"
        titles = soup.find_all("span", class_="entry-title p-name")
        print(f"Found {len(titles)} transcript titles.")

        # Attempt to find links associated with each title
        article_links = []
        base_url = "http://en.kremlin.ru"  # Base URL for constructing full links
        
        for title in titles:
            parent = title.find_parent("a")  # Find the parent <a> tag (link) if it exists
            if parent and 'href' in parent.attrs:
                relative_url = parent['href']  # Get the href attribute (the link)
                # Ensure the URL is properly constructed by removing duplicate path parts
                if not relative_url.startswith("http"):
                    # Correctly format relative links
                    full_url = base_url + relative_url
                else:
                    full_url = relative_url
                
                # Clean up any extra paths or repetitions in the link (e.g., duplicates like "/events/president/transcripts/events/...")
                if "/events/president/transcripts/events" in full_url:
                    full_url = full_url.replace("/events/president/transcripts/events", "/events/president/transcripts")

                article_links.append(full_url)

        print(f"Found {len(article_links)} article links.")
        return article_links
    finally:
        driver.quit()


# Function to scrape content from each individual page, focusing on specific elements
def scrape_individual_page(url, browser="chrome"):
    driver = get_browser_driver(browser)

    try:
        # Load the page
        driver.get(url)
        time.sleep(2)
        html = driver.page_source
        
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Extract the title (h1 element with class "entry-title")
        title_element = soup.find("h1", class_="entry-title p-name")
        title = title_element.get_text(strip=True) if title_element else "No title found"

        # Extract the summary (div with class "read__lead entry-summary")
        summary_element = soup.find("div", class_="read__lead entry-summary p-summary")
        summary = summary_element.get_text(strip=True) if summary_element else "No summary found"

        # Extract the main content (div with class "entry-content")
        content_element = soup.find("div", class_="entry-content e-content read__internal_content")
        # Get all paragraph <p> tags inside this div for the speech content
        paragraphs = content_element.find_all("p") if content_element else []
        content = "\n\n".join(p.get_text(strip=True) for p in paragraphs)

        # Return the extracted title, summary, and content
        return {
            "title": title,
            "summary": summary,
            "content": content if content else "No content found"
        }
    finally:
        driver.quit()


# Function to extract only the <body> content from the raw HTML
def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    return str(body_content) if body_content else ""

# Function to clean the extracted <body> content by removing <script> and <style> tags
def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )
    return cleaned_content

# Function to split the cleaned content into chunks, respecting LLM input size limits
def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i: i + max_length]
        for i in range(0, len(dom_content), max_length)
    ]
