from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import logging
import time
import streamlit as st
from scrape import scrape_all_links, scrape_individual_page, split_dom_content
from parse import parse_with_groq
from datetime import datetime
import threading

# Set the title of the Streamlit app
st.title("AI Web Scraper")

# Event for controlling scraping state
stop_event = threading.Event()

# Option to input a URL or upload a .txt file
option = st.selectbox("Choose an option:", ["Scrape from URL", "Upload .txt File"])

# Selectbox for browser choice
browser_choice = st.selectbox("Select browser for scraping:", ("Chrome", "Firefox"))

# Date input fields to set month and year limit (only visible for URL option)
if option == "Scrape from URL":
    end_month = st.selectbox("End Month:", range(1, 13), format_func=lambda x: datetime(1, x, 1).strftime('%B'))
    end_year = st.number_input("End Year:", min_value=2000, max_value=datetime.now().year, value=datetime.now().year)

# Initialize session state for storing data
if 'dom_content' not in st.session_state:
    st.session_state.dom_content = ""

if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = []

# Function to check if scraping should continue
def should_continue():
    return not stop_event.is_set()

# Stop Scraping button
if st.button("Stop Scraping"):
    stop_event.set()  # Signal to stop scraping

# Save progress after stopping or completion
if stop_event.is_set() or st.session_state.scraped_data:
    json_data = json.dumps(st.session_state.scraped_data, ensure_ascii=False, indent=4)
    with open("scraped_content.json", "w", encoding='utf-8') as f:
        f.write(json_data)
    st.success("Scraping stopped. Progress saved.")

# Download JSON button (enabled only when there is scraped data)
if "scraped_data" in st.session_state and len(st.session_state.scraped_data) > 0:
    json_data = json.dumps(st.session_state.scraped_data, ensure_ascii=False, indent=4)
    st.download_button(
        label="Download Scraped Content as JSON",
        data=json_data.encode('utf-8'),
        file_name="scraped_content.json",
        mime="application/json"
    )

# Section for scraping from a URL
if option == "Scrape from URL":
    url = st.text_input("Enter a website URL:", value="http://en.kremlin.ru/events/president/transcripts")  # Default URL

    # Scrape Site button for URL input
    if st.button("Scrape Site"):
        if url:  # Check if a URL was provided
            stop_event.clear()  # Reset stop event before starting new scrape
            st.write(f"Scraping the website using {browser_choice}...")
            st.write("Extracting links to individual transcripts...")

            # Scrape links up to the specified month and year
            article_links = scrape_all_links(url, browser=browser_choice.lower(), end_month=end_month, end_year=end_year)

            logging.info("Article links found: %s", article_links)

            if article_links:  # Check if any links were found
                st.write(f"Found {len(article_links)} transcript links.")
                st.session_state.article_links = article_links

                # Display the list of links in a collapsible expander
                with st.expander("View Transcript Links"):
                    for link in article_links:
                        st.write(link)

                # Use ThreadPoolExecutor for concurrent scraping of individual pages
                with ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_link = {executor.submit(scrape_individual_page, link, browser_choice.lower()): link for link in article_links}

                    for future in as_completed(future_to_link):
                        if stop_event.is_set():
                            logging.info("Stopping scraping as requested by user.")
                            break  # Exit if scraping is stopped

                        link = future_to_link[future]
                        try:
                            transcript_data = future.result()
                            title = transcript_data.get("title", "No Title")
                            summary = transcript_data.get("summary", "No Summary")
                            content = transcript_data.get("content", "No Content")

                            # Append the transcript's data as a dictionary to the scraped_data list
                            st.session_state.scraped_data.append({
                                "title": title,
                                "summary": summary,
                                "content": content
                            })

                            # Display the cleaned transcript in an expander
                            with st.expander(f"View Transcript Content - {title}"):
                                st.subheader(f"Transcript: {title}")
                                st.write(f"**Summary:** {summary}")
                                st.text_area("Transcript", content, height=300)

                        except Exception as e:
                            logging.error(f"Error scraping {link}: {e}")
                            st.write(f"Error scraping {link}: {e}")

                logging.info("Scraping session completed. Total links collected: %d", len(st.session_state.scraped_data))
            else:
                st.warning("No valid URLs found from the provided base URL.")
        else:
            st.warning("Please enter a valid URL.")

# Section for uploading .txt file with URLs
elif option == "Upload .txt File":
    uploaded_file = st.file_uploader("Upload a .txt file with URLs:", type=["txt"])

    # Scrape Site button for file upload input
    if uploaded_file is not None:
        # Read the uploaded file and extract URLs
        urls = uploaded_file.read().decode('utf-8').splitlines()
        urls = [url.strip() for url in urls if url.strip()]  # Clean the URLs

        logging.info("URLs loaded from file: %s", urls)

        if urls:  # Check if any links were found
            stop_event.clear()  # Reset stop event before starting new scrape

            st.write(f"Found {len(urls)} transcript links.")
            st.session_state.article_links = urls

            # Display the list of links in a collapsible expander
            with st.expander("View Transcript Links"):
                for link in urls:
                    st.write(link)

            # Use ThreadPoolExecutor for concurrent scraping of individual pages
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_link = {
                    executor.submit(scrape_individual_page, link, browser_choice.lower(), stop_event): link 
                    for link in urls 
                }

                for future in as_completed(future_to_link):
                    if stop_event.is_set():
                        logging.info("Stopping scraping as requested by user.")
                        break  # Exit the loop if scraping is stopped

                    link = future_to_link[future]
                    try:
                        transcript_data = future.result()
                        if not transcript_data:
                            continue

                        # Append the transcript's data to the scraped_data list
                        st.session_state.scraped_data.append(transcript_data)

                        # Display the cleaned transcript in an expander
                        with st.expander(f"View Transcript Content - {transcript_data['title']}"):
                            st.subheader(f"Transcript: {transcript_data['title']}")
                            st.write(f"**Summary:** {transcript_data['summary']}")
                            st.text_area("Transcript", transcript_data['content'], height=300)

                    except Exception as e:
                        logging.error(f"Error scraping {link}: {e}")
                        st.write(f"Error scraping {link}: {e}")

            logging.info("Scraping session completed. Total links collected: %d", len(st.session_state.scraped_data))
        else:
            st.warning("No valid URLs found in the uploaded file.")
else:
    if option == "Upload .txt File":
        st.warning("Please upload a .txt file containing URLs.")

# Parsing section (remains unchanged)
if "saved_dom_content" in st.session_state and st.session_state.saved_dom_content:
    parse_description = st.text_area(
        "Describe what you want to parse:",
        value="Analyze speeches:"
    )

    if st.button("Parse Content"):
        if parse_description:
            logging.info("Parsing content")
            dom_chunks = split_dom_content(st.session_state.saved_dom_content)
            if dom_chunks:
                result = parse_with_groq(dom_chunks, parse_description)
                st.write(result)