import streamlit as st
import openai

# Set your OpenAI API key (securely – environment variables are best)
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Access from Streamlit secrets

def analyze_links(urls):
    keywords = []
    for url in urls:
        try:
            prompt = f"Extract the most common and important keywords related to the main topics discussed on this webpage: {url}.  Return a list of keywords separated by commas."
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
            )
            extracted_keywords = completion.choices[0].message.content.split(",")
            keywords.extend([keyword.strip() for keyword in extracted_keywords])
        except Exception as e:
            st.error(f"Error analyzing URL {url}: {e}")
    return keywords

st.title("Priority Map")

links = []
for i in range(5):  # Allow up to 5 links
    link = st.text_input(f"Enter URL {i+1} (optional)", key=f"link_{i}")
    if link:
        links.append(link)

if st.button("Analyze Links") and links:
    if not 1 <= len(links) <=5:
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
