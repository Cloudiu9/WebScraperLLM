# WebScraperLLM

**WebScraperLLM** is a Python-based project for scraping data from websites using a combination of **Selenium**, **BeautifulSoup**, and **Streamlit**, with the ability to pass the extracted data to a **Large Language Model (LLM)** for further processing.  
This project was developed following [this tutorial](https://www.youtube.com/watch?v=Oo8-nEuDBkk).

## Features

- Scrapes web pages using **Selenium** for browser automation and **BeautifulSoup** for HTML parsing.
- Utilizes `chromedriver.exe` to automate interactions with the Chrome browser.
- Parses and extracts data into a structured format, which can then be processed by an LLM (e.g., using **Ollama**).
- Easy-to-use **Streamlit** interface for running the scraper and viewing the results.

## Prerequisites

- **Python 3.x**
- **Google Chrome** or **Firefox** browser installed
- A Large Language Model, such as [Ollama](https://ollama.com/download/windows)
- `chromedriver.exe` (included in the project or available via [ChromeDriver download](https://googlechromelabs.github.io/chrome-for-testing/#stable))
- `geckodriver.exe`(included in the project or available via [GeckoDriver download](https://github.com/mozilla/geckodriver/releases))

## Installation

1.  **Set up a virtual environment** (optional but recommended):
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

3. **Install the dependencies listed in requirements.txt**:
    ```bash
    pip install -r requirements.txt
    
4. **Set up chromedriver.exe and geckodriver.exe**:
- Ensure that chromedriver.exe and geckodriver.exe are in the project directory or added to your system's PATH.

5. **Download an [Ollama version](https://github.com/ollama/ollama)**

## Usage
- Run the scraper using Streamlit:

    ```bash
    streamlit run main.py
