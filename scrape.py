from datetime import datetime
import logging
import selenium.webdriver as webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent


# Initialize global variables for scraping
stopped = False

def get_browser_driver(browser='chrome'):
    if browser.lower() == 'chrome':
        chrome_options = ChromeOptions()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
        print("Initializing Chrome WebDriver...")
        return webdriver.Chrome(options=chrome_options)
    elif browser.lower() == 'firefox':
        firefox_options = FirefoxOptions()
        firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
        print("Initializing Firefox WebDriver...")
        return webdriver.Firefox(options=firefox_options)
    else:
        raise ValueError("Unsupported browser! Choose 'chrome' or 'firefox'.")
    
def create_driver(browser='chrome'):
    ua = UserAgent()
    user_agent = ua.random
    print(f"Using User-Agent: {user_agent}")

    if browser.lower() == 'chrome':
        options = ChromeOptions()
        options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Chrome(options=options)
        print("Chrome WebDriver initialized.")
    
    elif browser.lower() == 'firefox':
        # Create Firefox profile
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", user_agent)
        profile.set_preference("network.http.sendRefererHeader", 1)
        profile.set_preference("network.http.use-cache", False)
        
        # Set additional Firefox options
        options = FirefoxOptions()
        options.profile = profile  # Assign profile to FirefoxOptions
        options.set_preference("dom.webdriver.enabled", False)  # Disable webdriver flag
        options.set_preference("useAutomationExtension", False)  # Remove automation flag
        options.set_preference("marionette.logging", False)

        # Initialize WebDriver with options
        driver = webdriver.Firefox(options=options)
        print("Firefox WebDriver initialized.")
    
    else:
        raise ValueError("Unsupported browser! Choose 'chrome' or 'firefox'.")

    return driver

import requests

def get_free_proxy():
    """
    Fetches a free proxy from 'https://free-proxy-list.net/'.
    Returns a valid proxy if available, or None if no proxies are working.
    """
    url = "https://free-proxy-list.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    proxy_list = []

    # Scrape proxy table
    rows = soup.select("table#proxylisttable tbody tr")
    for row in rows:
        cols = row.find_all("td")
        ip = cols[0].get_text()
        port = cols[1].get_text()
        https = cols[6].get_text()
        if https == "yes":  # Only use HTTPS proxies
            proxy_list.append(f"{ip}:{port}")

    for proxy in proxy_list:
        try:
            # Test the proxy
            response = requests.get(
                "https://httpbin.org/ip",
                proxies={"http": f"http://{proxy}", "https": f"https://{proxy}"},
                timeout=3,
            )
            if response.status_code == 200:
                print(f"Using Proxy: {proxy}")
                return proxy
        except Exception:
            continue  # Skip non-working proxies

    return None

def create_driver_with_proxy(browser='chrome'):
    ua = UserAgent()
    user_agent = ua.random
    proxy = get_free_proxy()  # Get a proxy

    if not proxy:
        print("No working proxies found.")
        return create_driver(browser)  # Fallback to standard driver

    if browser.lower() == 'chrome':
        options = ChromeOptions()
        options.add_argument(f"user-agent={user_agent}")
        options.add_argument(f"--proxy-server={proxy}")
        driver = webdriver.Chrome(options=options)
        print(f"Chrome WebDriver initialized with proxy: {proxy}")
    
    elif browser.lower() == 'firefox':
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", user_agent)
        profile.set_preference("network.http.sendRefererHeader", 1)
        profile.set_preference("network.http.use-cache", False)
        
        # Set proxy
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", proxy.split(':')[0])
        profile.set_preference("network.proxy.http_port", int(proxy.split(':')[1]))
        profile.set_preference("network.proxy.ssl", proxy.split(':')[0])
        profile.set_preference("network.proxy.ssl_port", int(proxy.split(':')[1]))

        options = FirefoxOptions()
        options.profile = profile
        driver = webdriver.Firefox(options=options)
        print(f"Firefox WebDriver initialized with proxy: {proxy}")
    
    else:
        raise ValueError("Unsupported browser! Choose 'chrome' or 'firefox'.")

    return driver

def scrape_all_links(url, browser='chrome', end_month=None, end_year=None, delay_range=(3, 5)):
    """ 
    Scrapes all article links from the given URL until the specified end_month and end_year are reached.
    
    Parameters:
    - url (str): The URL to scrape links from.
    - browser (str): The browser to use ('chrome' or 'firefox').
    - end_month (int): The target end month (1 = January, ..., 12 = December).
    - end_year (int): The target end year.
    - delay_range (tuple): A tuple specifying the minimum and maximum delay in seconds.
    
    Returns:
    - list: A list of unique article links.
    """
    try:
        driver = get_browser_driver(browser)  # Initialize WebDriver
        driver.get(url)
        all_links = set()
        base_url = "http://en.kremlin.ru"
        
        while True:
            # Wait for the page to load and get the source
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # Random delay to mimic human browsing
            time.sleep(random.uniform(1, 2))
            
            # Collect article links
            titles = soup.find_all("span", class_="entry-title p-name")
            for title in titles:
                parent = title.find_parent("a")
                if parent and 'href' in parent.attrs:
                    relative_url = parent['href']
                    full_url = relative_url if relative_url.startswith("http") else f"{base_url}{relative_url}"
                    all_links.add(full_url)

            logging.info("Collected %d article links so far.", len(all_links))

            # Check if end date is reached (as before)
            found_valid_date = False
            if end_month and end_year:
                date_blocks = soup.find_all("a", class_="dateblock")
                for date_block in date_blocks:
                    date_text = date_block.get_text(strip=True).replace("Calendar:", "").strip()
                    try:
                        month_year = datetime.strptime(date_text, '%B, %Y')
                        if (month_year.year < end_year) or (month_year.year == end_year and month_year.month <= end_month):
                            found_valid_date = True
                            break
                    except ValueError:
                        logging.warning("Unrecognized date format: %s", date_text)
            
            if found_valid_date:
                logging.info("End date reached. Stopping scraping.")
                break
            
            # Extract current page number from URL
            current_page_number = int(url.split('/')[-1])  # Assuming url ends with /page/x
            next_page_number = current_page_number + 1
            
            # Construct new URL for next page
            url = f"http://en.kremlin.ru/events/president/transcripts/page/{next_page_number}"
            
            # Introduce a delay before loading the new URL
            delay_time = random.uniform(*delay_range)  # Random delay between specified range
            logging.info("Waiting for %.2f seconds before loading next page: %s", delay_time, url)
            time.sleep(delay_time)  # Wait before loading the new page
            
            # Load new URL instead of clicking 'Previous' button
            driver.get(url)
            logging.info("Navigated to next page: %s", url)

    except Exception as e:
        logging.error("An error occurred during scraping: %s", e)
    finally:
        driver.quit()  # Ensure driver is properly closed
        logging.info("Scraping session completed. Total links collected: %d", len(all_links))
    
    return list(all_links)

def fetch_page_with_retry(url, driver, stop_event, retries=3, delay=1):
    """
    Fetches a page with retries and a delay between requests.
    
    Parameters:
    - url (str): The URL of the page to fetch.
    - driver: The WebDriver instance being used.
    - stop_event: The threading event to check for stopping the scraper.
    - retries (int): The number of retry attempts.
    - delay (int): The delay between requests in seconds.
    
    Returns:
    - str: The page source if successful, None otherwise.
    """
    for attempt in range(retries):
        if stop_event.is_set():  # Check if scraping should stop
            logging.info("Stopping fetch_page_with_retry as requested by user.")
            return None  # Return None or handle accordingly if scraping is stopped

        try:
            driver.get(url)
            time.sleep(delay)  # Stagger requests to avoid overwhelming the server
            return driver.page_source
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed for {url}: {e}")
            time.sleep(delay * (attempt + 1))  # Exponential backoff

    return None

# Function to scrape content from each individual page, focusing on specific elements
def scrape_individual_page(url, browser="chrome", stop_event=None):
    if stop_event and stop_event.is_set():
        return None

    driver = get_browser_driver(browser)
    try:
        html = fetch_page_with_retry(url, driver, stop_event)
        if not html or (stop_event and stop_event.is_set()):
            return None

        # Scrape page content
        soup = BeautifulSoup(html, "html.parser")
        title_element = soup.find("h1", class_="entry-title p-name")
        title = title_element.get_text(strip=True) if title_element else "No title found"

        summary_element = soup.find("div", class_="read__lead entry-summary p-summary")
        summary = summary_element.get_text(strip=True) if summary_element else "No summary found"

        content_element = soup.find("div", class_="entry-content e-content read__internal_content")
        paragraphs = content_element.find_all("p") if content_element else []
        content = "\n\n".join(p.get_text(strip=True) for p in paragraphs) if paragraphs else "No content found"

        return {
            "title": title,
            "summary": summary,
            "content": content,
        }
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return None
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
