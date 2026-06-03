from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import logging
import time
import streamlit as st
from scrape import scrape_all_links, scrape_individual_page, split_dom_content
from parse import parse_with_groq
from datetime import datetime
import threading

st.markdown("""
<style>
/* ── BASE ───────────────────────────────────────────────────── */
html, body, .stApp {
    background-color: #09090f;
    color: #d8dce8;
    font-family: 'Courier New', Courier, monospace;
}
.block-container {
    padding-top: 2.5rem;
    max-width: 900px;
}
.stApp {
    background-image:
        radial-gradient(ellipse at top left,  rgba(160,0,0,0.08) 0%, transparent 55%),
        radial-gradient(ellipse at bottom right, rgba(20,40,90,0.18) 0%, transparent 60%);
}

/* ── TITLE ──────────────────────────────────────────────────── */
h1 {
    font-family: 'Courier New', Courier, monospace !important;
    color: #cc1111 !important;
    font-weight: 900 !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    text-shadow: 0 0 28px rgba(200,10,10,0.45);
    border-bottom: 2px solid #cc1111;
    padding-bottom: 0.4rem;
    margin-bottom: 0.2rem !important;
}
h2, h3 {
    color: #c9a84c !important;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-family: 'Courier New', Courier, monospace !important;
}

/* ── LABELS ─────────────────────────────────────────────────── */
label, .stSelectbox label, .stTextInput label,
.stTextArea label, .stNumberInput label {
    color: #8b9ab0 !important;
    font-family: 'Courier New', Courier, monospace !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
}

/* ── INPUTS ─────────────────────────────────────────────────── */
input, textarea {
    background-color: #10141f !important;
    color: #d8dce8 !important;
    border: 1px solid #2a3550 !important;
    border-radius: 2px !important;
    font-family: 'Courier New', Courier, monospace !important;
}
input:focus, textarea:focus {
    border-color: #cc1111 !important;
    box-shadow: 0 0 10px rgba(204,17,17,0.25) !important;
}

/* ── SELECTBOXES ─────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] input {
    background-color: #10141f !important;
    color: #d8dce8 !important;
    border: 1px solid #2a3550 !important;
    border-radius: 2px !important;
    font-family: 'Courier New', Courier, monospace !important;
}

/* ── BUTTONS ─────────────────────────────────────────────────── */
.stButton > button {
    background-color: #130000;
    color: #cc1111;
    border: 1px solid #cc1111;
    border-radius: 2px;
    font-family: 'Courier New', Courier, monospace;
    font-weight: bold;
    font-size: 0.82rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 0.5rem 1.4rem;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background-color: #cc1111;
    color: #f0f0f0;
    box-shadow: 0 0 18px rgba(204,17,17,0.5);
}
.stButton > button:active {
    background-color: #991010;
    transform: scale(0.98);
}

/* ── DOWNLOAD BUTTON ─────────────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background-color: #071207;
    color: #4caf50;
    border: 1px solid #4caf50;
    border-radius: 2px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.82rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    transition: all 0.2s ease;
}
[data-testid="stDownloadButton"] > button:hover {
    background-color: #4caf50;
    color: #09090f;
    box-shadow: 0 0 14px rgba(76,175,80,0.4);
}

/* ── EXPANDERS ───────────────────────────────────────────────── */
[data-testid="stExpander"] summary,
.streamlit-expanderHeader {
    background-color: #10141f !important;
    color: #c9a84c !important;
    border-left: 3px solid #cc1111 !important;
    font-family: 'Courier New', Courier, monospace !important;
    font-size: 0.82rem !important;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 0.6rem 1rem !important;
    border-radius: 2px !important;
}
[data-testid="stExpander"] {
    border: 1px solid #1e2535 !important;
    border-radius: 2px !important;
    background-color: #0d1019 !important;
}

/* ── ALERTS ──────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background-color: #071207 !important;
    border-left: 4px solid #4caf50 !important;
    border-radius: 2px !important;
    font-family: 'Courier New', Courier, monospace !important;
    font-size: 0.82rem;
    letter-spacing: 0.5px;
}
[data-testid="stAlert"][data-baseweb="notification"] p {
    color: #a8d5a2 !important;
}

/* ── WARNING ─────────────────────────────────────────────────── */
[data-testid="stAlert"].st-warning,
div.stWarning {
    border-left-color: #c9a84c !important;
    background-color: #12100a !important;
}

/* ── MARKDOWN TEXT ───────────────────────────────────────────── */
.stMarkdown p, .stMarkdown li {
    color: #9aa3b5;
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.88rem;
}

/* ── SCROLLBAR ───────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #09090f; }
::-webkit-scrollbar-thumb {
    background: #cc1111;
    border-radius: 2px;
}
</style>
""", unsafe_allow_html=True)

st.title("⬛ KREMLIN TRANSCRIPT INTELLIGENCE")
st.caption("CLASSIFIED — AUTOMATED TRANSCRIPT EXTRACTION SYSTEM · EYES ONLY")
st.markdown("---")

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
if stop_event and stop_event.is_set() or st.session_state.scraped_data:
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
    url = st.text_input(
        "Enter a website URL:",
        value="http://en.kremlin.ru/events/president/transcripts/page/1"
    )

    if st.button("Scrape Site"):
        if url:
            stop_event.clear()

            st.session_state.scraped_data = []
            st.session_state.saved_dom_content = ""

            st.write(f"Scraping the website using {browser_choice}...")
            st.write("Extracting links to individual transcripts...")

            article_links = scrape_all_links(
                url,
                browser=browser_choice.lower(),
                end_month=end_month,
                end_year=end_year
            )

            logging.info("Article links found: %s", article_links)

            if article_links:
                st.write(f"Found {len(article_links)} transcript links.")
                st.session_state.article_links = article_links

                with st.expander("View Transcript Links"):
                    for link in article_links:
                        st.write(link)

                with ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_link = {
                        executor.submit(
                            scrape_individual_page,
                            link,
                            browser_choice.lower(),
                            stop_event
                        ): link
                        for link in article_links
                    }

                    for future in as_completed(future_to_link):
                        if stop_event and stop_event.is_set():
                            logging.info("Stopping scraping as requested by user.")
                            break

                        link = future_to_link[future]
                        try:
                            transcript_data = future.result()
                            if not transcript_data:
                                continue

                            title = transcript_data.get("title", "No Title")
                            summary = transcript_data.get("summary", "No Summary")
                            content = transcript_data.get("content", "No Content")

                            st.session_state.scraped_data.append({
                                "title": title,
                                "summary": summary,
                                "content": content
                            })

                            with st.expander(f"View Transcript Content - {title}"):
                                st.subheader(f"Transcript: {title}")
                                st.write(f"**Summary:** {summary}")
                                st.text_area("Transcript", content, height=300)

                        except Exception as e:
                            logging.error(f"Error scraping {link}: {e}")
                            st.write(f"Error scraping {link}: {e}")

                st.session_state.saved_dom_content = "\n\n".join(
                    item.get("content", "")
                    for item in st.session_state.scraped_data
                    if item.get("content")
                )

                logging.info(
                    "Scraping session completed. Total links collected: %d",
                    len(st.session_state.scraped_data)
                )
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
                    if stop_event and stop_event.is_set():
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