import json  # Import JSON module for file download
import streamlit as st
from scrape import scrape_all_links, scrape_individual_page, split_dom_content
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

# Initialize a button to stop scraping
if st.button("Stop Scraping"):
    if "scraped_data" in st.session_state:
        # Save the scraped content as JSON
        json_data = json.dumps(
            st.session_state.scraped_data,
            ensure_ascii=False,
            indent=4
        )
        with open("scraped_content.json", "w", encoding='utf-8') as f:
            f.write(json_data)
        st.success("Scraped content saved successfully.")
    else:
        st.warning("No data has been scraped yet.")

# Check if the "Scrape Site" button is clicked
if st.button("Scrape Site"):
    st.write(f"Scraping the website using {browser_choice}...")  # Display feedback when scraping starts

    # Scrape all links from the main page
    st.write("Extracting links to individual transcripts...")
    article_links = scrape_all_links(url, browser=browser_choice.lower())  # Scrape all links

    if article_links:
        st.write(f"Found {len(article_links)} transcript links.")
        st.session_state.article_links = article_links  # Store the article links in session state
        st.session_state.scraped_data = []  # Initialize an empty list to store scraped content

        # Display the list of links in a collapsible expander
        with st.expander("View Transcript Links"):
            for link in article_links:
                st.write(link)

        # Iterate through all the individual transcript links
        for i, link in enumerate(article_links):
            st.write(f"Scraping transcript {i + 1}/{len(article_links)}: {link}")

            # Scrape the content of the individual transcript page
            transcript_data = scrape_individual_page(link, browser=browser_choice.lower())

            # Extract the title, summary, and content from the transcript_data
            title = transcript_data.get("title", "No Title")
            summary = transcript_data.get("summary", "No Summary")
            content = transcript_data.get("content", "No Content")

            # Check for empty fields and warn if any are missing
            if title == "No Title" or summary == "No Summary" or content == "No Content":
                st.write("Warning: One of the fields is empty.")  # Warning message

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

            # Store the scraped content collected so far in session state
            st.session_state.dom_content = f"Title: {title}\n\nSummary: {summary}\n\n{content}\n\n"

            # Debugging line to check DOM content length
            st.write(f"DOM Content Length: {len(st.session_state.dom_content)}")  # Debug line

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
    st.write(f"DOM Content Length: {len(st.session_state.dom_content)}")  # Debug line

    # Input field for users to describe what specific information they want to extract
    parse_description = st.text_area(
        "Describe what you want to parse:",
        value="Extract details of each speech, including date, location, and main topics discussed, and organize them in a structured table format." # Default prompt
    )

    # Check if the "Parse Content" button is clicked
    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content")  # Display feedback when parsing starts

            # Split the stored DOM content into chunks (to avoid exceeding token limits in LLMs)
            dom_chunks = split_dom_content(st.session_state.dom_content)

            if not dom_chunks:
                st.write("No content to parse.")  # Check for empty chunks
            else:
                # Pass the DOM chunks and user-provided parse description to the LLM
                result = parse_with_groq(dom_chunks, parse_description)
                st.write(result)

