# function that takes an URL and returns all content from it

import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup # html parser

def scrape_website(website):
    print("Launching chrome browser...")

    chrome_driver_path = "./chromedriver.exe"
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

    try:
        # using driver to go to website --> grab
        driver.get(website)
        print("Page loaded...")
        html = driver.page_source

        return html
    finally:
        driver.quit()

# we need to remove css / js from scraper, so the LLM has an easier task

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

# look inside parsed content, remove <script> , <style> tags
def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # get all text ==> separate it with a new line
    cleaned_content = soup.get_text(separator="\n")

    # remove unnecessary \n content (empty strings)
    # if \n is not separating anything ==> remove it
    cleaned_content = "\n".join(line.strip() for line in cleaned_content.splitlines() if line.strip())

    return cleaned_content

# we need to split the text into different batches of what the maximum
# size of the LLM is (ex: 8000 characters token limit)

def split_dom_content(dom_content, max_length=6000):
    # grabs first 6000 characters ==> because of for loop, i is now 6000, goes to the next
    # 6000 characters, repeats until we reach length of dom_content
    return [
        dom_content[i: i+max_length] for i in range(0, len(dom_content), max_length)
    ]
