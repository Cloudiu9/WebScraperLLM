from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import logging
import streamlit as st
from scrape import scrape_all_links, scrape_individual_page, split_dom_content
from parse import parse_with_groq
from datetime import datetime

# Set the title of the Streamlit app
st.title("AI Web Scraper")

# Option to input a URL or upload a .txt file
option = st.selectbox("Choose an option:", ["Scrape from URL", "Upload .txt File"])

# Selectbox for browser choice
browser_choice = st.selectbox(
    "Select browser for scraping:",
    ("Chrome", "Firefox")
)

# Date input fields to set month and year limit
end_month = st.selectbox("End Month:", range(1, 13), format_func=lambda x: datetime(1, x, 1).strftime('%B'))
end_year = st.number_input("End Year:", min_value=2000, max_value=datetime.now().year, value=datetime.now().year)

# Initialize session state for storing data
if 'dom_content' not in st.session_state:
    st.session_state.dom_content = ""

if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = []

# Stop Scraping button
if st.button("Stop Scraping"):
    if st.session_state.scraped_data:
        json_data = json.dumps(st.session_state.scraped_data, ensure_ascii=False, indent=4)
        with open("scraped_content.json", "w", encoding='utf-8') as f:
            f.write(json_data)

        # Construct DOM content from scraped data
        st.session_state.dom_content = "\n".join(
            f"Title: {item['title']}\n\nSummary: {item['summary']}\n\n{item['content']}\n\n"
            for item in st.session_state.scraped_data
        )

        # Save the constructed DOM content
        if st.session_state.dom_content:
            st.session_state.saved_dom_content = st.session_state.dom_content
            st.success("Scraped content saved successfully, including total DOM content.")
        else:
            st.warning("No DOM content available to save.")
    else:
        st.warning("No data has been scraped yet.")

# Section for scraping from a URL
if option == "Scrape from URL":
    url = st.text_input(
        "Enter a website URL:",
        value="http://en.kremlin.ru/events/president/transcripts"  # Default URL
    )

    # Scrape Site button for URL input
    if st.button("Scrape Site"):
        if url:  # Check if a URL was provided
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
                with ThreadPoolExecutor(max_workers=5) as executor:
                    future_to_link = {executor.submit(scrape_individual_page, link, browser_choice.lower()): link for link in article_links}

                    for future in as_completed(future_to_link):
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
                            st.write(f"Error scraping {link}: {e}")
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

        # Clean the URLs: strip whitespace and filter out empty strings
        urls = [url.strip() for url in urls if url.strip()]

        logging.info("URLs loaded from file: %s", urls)

        if urls:  # Check if any links were found
            st.write(f"Found {len(urls)} transcript links.")
            st.session_state.article_links = urls

            # Display the list of links in a collapsible expander
            with st.expander("View Transcript Links"):
                for link in urls:
                    st.write(link)

            # Use ThreadPoolExecutor for concurrent scraping of individual pages
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_link = {executor.submit(scrape_individual_page, link, browser_choice.lower()): link for link in urls}

                for future in as_completed(future_to_link):
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
                        st.write(f"Error scraping {link}: {e}")
        else:
            st.warning("No valid URLs found in the uploaded file.")
    else:
        if option == "Upload .txt File":
            st.warning("Please upload a .txt file containing URLs.")

# Store DOM content in session state
st.session_state.dom_content = "\n".join(
    f"Title: {item['title']}\n\nSummary: {item['summary']}\n\n{item['content']}\n\n"
    for item in st.session_state.scraped_data
)

# Download JSON button
if "scraped_data" in st.session_state and st.session_state.scraped_data:
    json_data = json.dumps(st.session_state.scraped_data, ensure_ascii=False, indent=4)
    st.download_button(
        label="Download Scraped Content as JSON",
        data=json_data.encode('utf-8'),
        file_name="scraped_content.json",
        mime="application/json"
    )

# Parsing section
if "saved_dom_content" in st.session_state and st.session_state.saved_dom_content:
    st.write(f"DOM Content Length: {len(st.session_state.saved_dom_content)}")
    
    parse_description = st.text_area(
        "Describe what you want to parse:",
        value="Analyze speeches:"
    )

    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content")
            dom_chunks = split_dom_content(st.session_state.saved_dom_content)

            if dom_chunks:
                result = parse_with_groq(dom_chunks, parse_description)
                st.write(result)