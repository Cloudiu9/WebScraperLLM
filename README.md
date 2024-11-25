# WebScraperLLM

## This project is for educational purposes only. Users are responsible for complying with the terms of service of any website they interact with. ##

**WebScraperLLM** is a Python-based project for scraping data from websites using **Selenium**, **BeautifulSoup**, and **Streamlit**, with the ability to pass extracted data to a **Large Language Model (LLM)** for further processing. The foundation of this project was developed following [this tutorial](https://www.youtube.com/watch?v=Oo8-nEuDBkk).

## Features

- Scrapes entire website sections by following and scraping every individual page, allowing for comprehensive data collection.
- Uses **Selenium** for browser automation and **BeautifulSoup** for HTML parsing.
- Supports both **Chrome** and **Firefox** browsers.
- Allows parsed data to be processed by an LLM, now supporting **Groq's API LLM** integration for enhanced flexibility in processing data in the cloud, in addition to local LLMs.
- Streamlit-powered user interface for seamless scraping, previewing, and downloading of results.

## Prerequisites

- **Python 3.x**
- **Google Chrome** or **Firefox** browser installed
- A Large Language Model, such as [Groq’s API LLM](https://groq.com/api) or [Ollama](https://ollama.com/download/windows)
- `chromedriver.exe` and `geckodriver.exe` (included in the project or available via [ChromeDriver download](https://googlechromelabs.github.io/chrome-for-testing/#stable) and [GeckoDriver download](https://github.com/mozilla/geckodriver/releases))
- **New Libraries**:
  - **Groq** API library for cloud-based LLM processing (see installation below)

## Installation

1. **Set up a virtual environment** (optional but recommended):

   ```bash
   python -m venv ai
   .\ai\Scripts\activate.bat  # On Windows
   # OR
   source ai/bin/activate  # On macOS/Linux
   ```

2. **Clone the repository**:

   ```bash
   git clone https://github.com/Cloudiu9/WebScraperLLM.git
   cd WebScraperLLM
   ```

3. **Install the dependencies listed in requirements.txt**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Install the Groq API library** (if not included in requirements.txt):

   ```bash
   pip install groq  # or `pip install <groq-library-package>` if named differently
   ```

5. **Set up chromedriver.exe and geckodriver.exe**:

   Ensure that `chromedriver.exe` and `geckodriver.exe` are in the project directory or added to your system's PATH.

6. **Set up the LLM**:

   - **Groq's API**: Register for a Groq API key at [Groq's API](https://console.groq.com/keys) and add it to your project’s environment variables or input it into your configuration.
   - **Ollama**: Download an [Ollama version](https://github.com/ollama/ollama) as an alternative LLM.

## Usage

- Run the scraper using Streamlit:

  ```bash
  streamlit run main.py
  ```

## Example Workflow

- Enter a website URL with a structure similar to http://example.com/events/category/transcripts in the Streamlit interface to begin scraping. Ensure the site you use follows a consistent format for event and transcript pages to work effectively with this scraper.
- Select the browser (Chrome or Firefox).
- Start scraping, and the scraper will collect data from all individual pages linked from the main URL.
- Parse and process the scraped data with Groq's API LLM, directly from the interface, for advanced text analysis or summarization.
- Download scraped content as a JSON file if needed.
- Run the **sortJSON.py** file to sort the JSON file by date if needed.
