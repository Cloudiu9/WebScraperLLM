# streamlit --> easy way to create python web apps, easy to interact with LLMs
# selenium --> allows automation of a web browser ==> navigate to a page, grab everything there, filter data, pass into LLM

import streamlit as st
from scrape import scrape_website, split_dom_content, clean_body_content, extract_body_content
from parse import parse_with_ollama

st.title("AI Web Scraper")
url = st.text_input("Enter a website URL: ")

if(st.button("Scrape Site")):
    st.write("Scraping the website")


    result = scrape_website(url)
    #print(result)
    
    body_content = extract_body_content(result)
    cleaned_content = clean_body_content(body_content)

    # store in the streamlit session to access later
    st.session_state.dom_content = cleaned_content

    # button expander text box to view more content
    with st.expander("View DOM Content"):
        st.text_area("DOM Content", cleaned_content, height=300)

# user prompt for LLM
# if we saved the content, 
if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe what you want to parse: ")

    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content")

            # pass chunks to LLM
            dom_chunks = split_dom_content(st.session_state.dom_content)
            result = parse_with_ollama(dom_chunks, parse_description)
            st.write(result)