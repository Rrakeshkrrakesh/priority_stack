import requests
import google.generativeai as genai
import os
import streamlit as st
import json
from collections import Counter

# Configure Gemini (replace with your actual API key or use Streamlit secrets)
api_key = st.secrets["GEMINI_API_KEY"]  # Or os.environ["API_KEY"] if not using Streamlit secrets
genai.configure(api_key=api_key)

def analyze_links(urls):
    all_keywords = []
    model = genai.GenerativeModel("gemini-1.5-flash")
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            webpage_content = response.text

            max_content_length = 2000000  # Adjust as needed
            truncated_content = webpage_content[:max_content_length]

            prompt = f"""
                Extract the most relevant keywords related to the main topics discussed on this webpage.
                Prioritize keywords that are central to the theme and purpose of the page.

                Webpage Content:
                ```html
                {truncated_content}
                ```

                Return a JSON array of strings (keywords).  Do not include any extra text or formatting, just the JSON array.
            """

            response = model.generate_content(prompt)

            try:
                # Remove potential problematic characters and whitespace
                cleaned_response = response.text.strip()
                if (cleaned_response.startswith("```") and cleaned_response.endswith("```")):
                    cleaned_response = cleaned_response[3:-3]
                extracted_keywords = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON for {url}. Error: {e}")
                st.write(f"Cleaned LLM response: {cleaned_response}")
                return None

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

st.title("Priority Map")

links = []
for i in range(2):  # Allow up to 2 links (adjust as needed)
    link = st.text_input(f"Enter URL {i+1} (optional)", key=f"link_{i}")
    if link:
        links.append(link)

if st.button("Analyze Links") and links:
    if not 1 <= len(links) <= 2:
        st.error("Please enter between 1 and 2 URLs")
    else:
        with st.spinner("Analyzing links..."):
            sorted_keywords = analyze_links(links)

        if sorted_keywords:
            top_keywords = [f"{keyword} ({count})" for keyword, count in sorted_keywords[:5]]
            st.write(", ".join(top_keywords))

            st.header("Prioritize Keywords")
            default_priorities = [keyword for keyword, count in sorted_keywords[:5]] if len(sorted_keywords) > 5 else [keyword for keyword, count in sorted_keywords]
            priorities = st.multiselect(
                "Select priorities (drag to reorder)", [keyword for keyword, count in sorted_keywords], default_priorities
            )

            st.write("Your prioritized keywords:")
            for i, keyword in enumerate(priorities):
                st.write(f"{i+1}. {keyword}")
