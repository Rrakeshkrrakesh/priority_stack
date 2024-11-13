import requests
import google.generativeai as genai
import os
import streamlit as st
import json
from collections import Counter
from bs4 import BeautifulSoup

# --- Configuration ---
api_key = st.secrets["GEMINI_API_KEY"]  # Or os.environ["API_KEY"] if not on Streamlit Cloud
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Helper Functions ---

def analyze_links(urls):
    all_keywords = []
    for url in urls:
        # ... (The code inside this function remains exactly the same as the previous version)


# --- Streamlit App ---
st.title("Priority Map")

# --- Bookmark/URL Input ---  (Combined for better UX)
if "links" not in st.session_state:
    st.session_state.links = []

uploaded_file = st.file_uploader("Upload Chrome bookmarks HTML file (optional)", type=["html"])
if uploaded_file:
    try:
        html_content = uploaded_file.read().decode("utf-8")
        soup = BeautifulSoup(html_content, 'html.parser')
        urls = [link.get('href') for link in soup.find_all('a') if link.get('href')]
        st.success("Bookmarks imported successfully!")
        st.session_state.links.extend(urls) # Add imported URLs to existing list
    except Exception as e:
        st.error(f"Error processing bookmarks file: {e}")


for i in range(5):  # Allow up to 5 URLs
    link = st.text_input(f"Enter URL {i+1} (optional)", key=f"link_{i}")
    if link and link not in st.session_state.links:  # Avoid duplicates
        st.session_state.links.append(link)


# --- Analysis and Display ---
if st.button("Analyze Links"):
    if not st.session_state.links or not 1 <= len(st.session_state.links) <= 5:  # Check if links exist in session state
        st.error("Please enter between 1 and 5 URLs or import from Bookmarks.")
    else:
        with st.spinner("Analyzing links..."):
            sorted_keywords = analyze_links(st.session_state.links)

        if sorted_keywords:
            top_keywords = [f"{keyword} ({count})" for keyword, count in sorted_keywords[:5]]
            st.write(", ".join(top_keywords))

            st.header("Prioritize Keywords")

            default_priorities = [keyword for keyword, count in sorted_keywords[:5]] if len(sorted_keywords) > 5 else [keyword for keyword, count in sorted_keywords]
            if "priorities" not in st.session_state:
                st.session_state.priorities = default_priorities

            priorities = st.multiselect(
                "Select priorities (drag to reorder)", [keyword for keyword, count in sorted_keywords], st.session_state.priorities
            )
            st.session_state.priorities = priorities


            st.write("Your prioritized keywords:")
            for i, keyword in enumerate(st.session_state.priorities):
                st.write(f"{i+1}. {keyword}")
