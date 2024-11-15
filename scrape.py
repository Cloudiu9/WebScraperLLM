from datetime import datetime
import logging
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import streamlit as st
from selenium import webdriver


# Initialize global variables for scraping
stopped = False

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


# Function to scrape each page's content
def scrape_individual_page(url, browser="chrome"):
    driver = get_browser_driver(browser)
    global stopped
    
    try:
        driver.get(url)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract elements
        title = soup.find("h1", class_="entry-title p-name").get_text(strip=True) if soup.find("h1", class_="entry-title p-name") else "No title found"
        summary = soup.find("div", class_="read__lead entry-summary p-summary").get_text(strip=True) if soup.find("div", class_="read__lead entry-summary p-summary") else "No summary found"
        content_element = soup.find("div", class_="entry-content e-content read__internal_content")
        content = "\n\n".join(p.get_text(strip=True) for p in content_element.find_all("p")) if content_element else "No content found"
        
        # Display content incrementally
        st.write(f"Extracted Title: {title}")
        st.write(f"Extracted Summary: {summary}")
        st.write(f"Extracted Content Length: {len(content)}")
        
        return {"title": title, "summary": summary, "content": content}
    except Exception as e:
        st.write(f"Error scraping {url}: {e}")
        return {"title": "Error", "summary": "Error", "content": "Error"}
    finally:
        driver.quit()
        if stopped:
            st.write("Scraping stopped by user.")


def scrape_all_links(url, browser='chrome', end_month=None, end_year=None):
    # Initialize WebDriver based on the selected browser
    if browser == 'chrome':
        driver = webdriver.Chrome()
    else:
        driver = webdriver.Firefox()

    driver.get(url)
    time.sleep(2)  # Allow time for page to load

    all_links = set()  # Use a set to avoid duplicates

    while True:
        # Extract page content
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Extract links from span elements with class "entry-title p-name"
        titles = soup.find_all("span", class_="entry-title p-name")
        base_url = "http://en.kremlin.ru"

        for title in titles:  # Collect all article links found on this page
            parent = title.find_parent("a")  # Find the parent <a> tag
            if parent and 'href' in parent.attrs:
                relative_url = parent['href']
                full_url = base_url + relative_url if not relative_url.startswith("http") else relative_url
                all_links.add(full_url)

        logging.info("Found %d article links on this page.", len(titles))

        # Check for the date block and see if it matches the criteria
        date_blocks = soup.find_all("a", class_="dateblock")
        
        found_valid_date = False
        
        for date_block in date_blocks:
            date_text = date_block.get_text(strip=True)  # Get the visible text
            logging.info("Found date block text: %s", date_text)

            try:
                month_year = datetime.strptime(date_text, '%B, %Y')
                if (month_year.year < end_year) or (month_year.year == end_year and month_year.month <= end_month):
                    found_valid_date = True
                    logging.info("Valid date found: %s", month_year)
                    break
            except ValueError:
                logging.warning("Date format not recognized: %s", date_text)

        if found_valid_date:
            break  # Exit loop if a valid date is found

        # Scroll down to load more articles if no valid date was found
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.more-next") 
            next_button.click()
            logging.info("Clicked on 'Next' button.")
            time.sleep(2)  # Wait for new content to load
            
        except Exception as e:
            logging.error("No more pages to load or error occurred: %s", e)
            break  # Exit loop if no more pages are available

    driver.quit()

    logging.info("Total article links collected: %d", len(all_links))
    return list(all_links)

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
