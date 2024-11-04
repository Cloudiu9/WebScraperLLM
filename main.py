import json  # Import JSON module for file download
import streamlit as st
from scrape import scrape_website, scrape_all_links, scrape_individual_page, split_dom_content
from parse import parse_with_groq

# Set the title of the Streamlit app
st.title("AI Web Scraper")

# Create an input field for the user to enter the URL of the website to scrape, with a default value
url = st.text_input(
    "Enter a website URL:",
    value="http://en.kremlin.ru/events/president/transcripts"  # Default URL
)

# Add a selectbox for the user to choose the browser (Chrome or Firefox)
browser_choice = st.selectbox(
    "Select browser for scraping:",
    ("Chrome", "Firefox")
)

# Check if the "Scrape Site" button is clicked
if st.button("Scrape Site"):
    st.write(f"Scraping the website using {browser_choice}...")  # Display feedback when scraping starts

    # Step 1: Scrape all links from the main page
    st.write("Extracting links to individual transcripts...")
    article_links = scrape_all_links(url, browser=browser_choice.lower())  # Scrape all links

    if article_links:
        st.write(f"Found {len(article_links)} transcript links.")
        st.session_state.article_links = article_links  # Store the article links in session state
        st.session_state.stop_scraping = False  # Initialize or reset the stop flag
        st.session_state.scraped_data = []  # Initialize an empty list to store scraped content

        # Display the list of links in a collapsible expander
        with st.expander("View Transcript Links"):
            for link in article_links:
                st.write(link)

    else:
        st.write("No transcript links found.")

# Check if article links have been stored in the session
if "article_links" in st.session_state:
    # Step 2: Scrape individual pages based on the links
    st.write("Scraping individual transcript pages...")
    
    # Add a Stop Scraping button
    if st.button("Stop Scraping"):
        st.session_state.stop_scraping = True  # Set the stop flag to True when clicked

    all_cleaned_content = ""

    for idx, link in enumerate(st.session_state.article_links):
        # Check if stop flag is set
        if st.session_state.get("stop_scraping"):
            st.write("Scraping has been stopped.")
            break  # Exit the loop if stop flag is True

        st.write(f"Scraping transcript {idx + 1}: {link}")

        # Scrape the content of the individual transcript page
        transcript_data = scrape_individual_page(link, browser=browser_choice.lower())
        
        # Extract the title, summary, and content from the transcript_data
        title = transcript_data["title"]
        summary = transcript_data["summary"]
        # Replace "\n" with real line breaks in `content`
        content = transcript_data["content"]

        # Append each transcript's data as a dictionary to the scraped_data list
        st.session_state.scraped_data.append({
            "title": title,
            "summary": summary,
            "content": content
        })

        # Append the cleaned content (title + summary + content) to the cumulative string for further processing
        all_cleaned_content += f"Title: {title}\n\nSummary: {summary}\n\n{content}\n\n"

        # Display each cleaned transcript in an expander
        with st.expander(f"View Transcript {idx + 1} Content"):
            st.subheader(f"Transcript {idx + 1}: {title}")
            st.write(f"**Summary:** {summary}")
            st.text_area(f"Transcript {idx + 1}", content, height=300)

    # Store the scraped content collected so far in session state
    st.session_state.dom_content = all_cleaned_content

    # Provide a download button for the scraped content as a JSON file if there’s content
    if st.session_state.scraped_data:
        # Format JSON with proper line breaks and indentation
        json_data = json.dumps(
            st.session_state.scraped_data, 
            ensure_ascii=False,  # Keep special characters as they are
            indent=4  # Use indentation for better readability
        )
        st.download_button(
            label="Download Scraped Content as JSON",
            data=json_data.encode('utf-8'),  # Encode to utf-8 for compatibility
            file_name="scraped_content.json",
            mime="application/json"
        )

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
            result = parse_with_groq(dom_chunks, parse_description)

            # Display the result returned by the LLM after parsing the content
            st.write(result)