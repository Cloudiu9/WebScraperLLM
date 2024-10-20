# Import necessary libraries for the app
# Streamlit: for creating a simple web interface in Python, which is great for interacting with LLMs
# Selenium: for automating a web browser, used to scrape websites, grab page content, and pass it to the LLM

import streamlit as st
from scrape import scrape_website, split_dom_content, clean_body_content, extract_body_content
from parse import parse_with_ollama

# Set the title of the Streamlit app
st.title("AI Web Scraper")

# Create an input field for the user to enter the URL of the website to scrape
url = st.text_input("Enter a website URL:")

# Add a selectbox for the user to choose the browser (Chrome or Firefox)
browser_choice = st.selectbox(
    "Select browser for scraping:",
    ("Chrome", "Firefox")
)

# Check if the "Scrape Site" button is clicked
if st.button("Scrape Site"):
    st.write(f"Scraping the website using {browser_choice}...")  # Display feedback when scraping starts

    # Call the scrape_website function to get the raw HTML content of the website, passing the browser choice
    result = scrape_website(url, browser=browser_choice.lower())  # Lowercase to match the scrape.py function

    # Extract the <body> content from the HTML (removes headers, footers, etc.)
    body_content = extract_body_content(result)

    # Clean the body content by removing unwanted tags like <script> and <style>
    cleaned_content = clean_body_content(body_content)

    # Store the cleaned DOM content in the session state to access it later during parsing
    st.session_state.dom_content = cleaned_content

    # Display the cleaned DOM content in a collapsible expander for users to review
    with st.expander("View DOM Content"):
        # Display the cleaned DOM content in a text area (with a max height of 300px)
        st.text_area("DOM Content", cleaned_content, height=300)

# User input for describing what they want to parse from the content
# This block checks if the content has been saved in the session
if "dom_content" in st.session_state:
    # Input field for users to describe what specific information they want to extract
    parse_description = st.text_area("Describe what you want to parse:")

    # Check if the "Parse Content" button is clicked
    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content")  # Display feedback when parsing starts

            # Split the stored DOM content into chunks (to avoid exceeding token limits in LLMs)
            dom_chunks = split_dom_content(st.session_state.dom_content)

            # Pass the DOM chunks and user-provided parse description to the LLM
            result = parse_with_ollama(dom_chunks, parse_description)

            # Display the result returned by the LLM after parsing the content
            st.write(result)
