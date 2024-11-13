import requests
import google.generativeai as genai
import os
import streamlit as st

# Configure Gemini (replace with your actual API key or use Streamlit secrets)
api_key = st.secrets["GEMINI_API_KEY"] # Or os.environ["API_KEY"]
genai.configure(api_key=api_key)

def analyze_links(urls):
    keywords = []
    model = genai.GenerativeModel("gemini-1.5-flash")  # Or a suitable Gemini model
    for url in urls:
        try:
            response = requests.get(url, timeout=10) # Add a timeout to prevent indefinite hanging
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            webpage_content = response.text

            # Limit content size to prevent exceeding LLM token limits
            max_content_length = 20000000000  # Adjust as needed
            truncated_content = webpage_content[:max_content_length]


            prompt = f"""
                Extract the most common and important keywords related to the main topics discussed on this webpage:

                ```html
                {truncated_content}
                ```

                Return a list of keywords separated by commas.
            """

            response = model.generate_content(prompt)
            extracted_keywords = response.text.split(",")
            keywords.extend([keyword.strip() for keyword in extracted_keywords])

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching URL {url}: {e}")
        except Exception as e:
            st.error(f"Error analyzing URL {url}: {e}")
    return keywords






st.title("Priority Map")

links = []
for i in range(2):  # Allow up to 5 links
    link = st.text_input(f"Enter URL {i+1} (optional)", key=f"link_{i}")
    if link:
        links.append(link)

if st.button("Analyze Links") and links:
    if not 1 <= len(links) <=2:
        st.error("Please enter between 1 and 5 URLs")
    else:
      with st.spinner("Analyzing links..."):
          keywords = analyze_links(links)

      if keywords:
          st.header("Extracted Keywords")
          st.write(", ".join(keywords))

          st.header("Prioritize Keywords")
          priorities = st.multiselect(
              "Select priorities (drag to reorder)", keywords, keywords
          )


          st.write("Your prioritized keywords:")
          for i, keyword in enumerate(priorities):
              st.write(f"{i+1}. {keyword}")
