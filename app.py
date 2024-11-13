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
        try:
            # 1. Fetch webpage content
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            webpage_content = response.text

            # 2. Truncate content
            max_content_length = 2000000  # Adjust if needed
            truncated_content = webpage_content[:max_content_length]

            # 3. Construct prompt
            prompt = f"""
                Extract the most relevant keywords related to the main topics discussed on this webpage.
                Prioritize keywords that are central to the theme and purpose of the page.

                Webpage Content:
                ```html
                {truncated_content}
                ```

                Return a JSON array of strings (keywords). Do not include any extra text or formatting, just the JSON array.
            """

            # 4. LLM Interaction
            response = model.generate_content(prompt)

            # 5. Parse JSON response
            try:
                cleaned_response = response.text.strip()
                if (cleaned_response.startswith("```") and cleaned_response.endswith("```")):
                    cleaned_response = cleaned_response[3:-3]
                extracted_keywords = json.loads(cleaned_response)
                print(f"Extracted keywords for {url}: {extracted_keywords}")
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON for {url}. Error: {e}")
                st.write(f"Cleaned LLM response: {cleaned_response}")
                return None

            # 6. Validate and append keywords
            if isinstance(extracted_keywords, list) and all(isinstance(keyword, str) for keyword in extracted_keywords):
                all_keywords.extend(extracted_keywords)
            else:
                st.warning(f"Keywords not a list of strings for URL: {url}")

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching URL {url}: {e}")
        except Exception as e:
            st.error(f"Error analyzing URL {url}: {e}")

    keyword_counts = Counter(all_keywords)
    sorted_keywords = sorted(keyword_counts.items(), key=lambda item: item[1], reverse=True)
    return sorted_keywords

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

print(f"st.session_state.links: {st.session_state.links}")

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
