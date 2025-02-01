import streamlit as st
import requests
from bs4 import BeautifulSoup
from common import api_interaction

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()

def summarize(api_choice, text):
    return api_interaction.getAIResponse(api_choice," i have this site, please : \n extract a detailed summary \n set the summary language base on the content of the site \n\n this is the site", text)

st.title("Website Summarizer")

with st.form(key='summarize_form'):
    url = st.text_input("Enter a website URL:")
    summarization_option = st.radio("Choose summarization method:", ("OpenAI", "Claude"))
    submit_button = st.form_submit_button(label="Summarize")

if submit_button and url and summarization_option:
    with st.spinner("Summarizing..."):
        scraped_text = scrape_website(url)

        if summarization_option == "OpenAI":
            summary = summarize("OpenAI", scraped_text)
        elif summarization_option == "Claude":
            summary = summarize("Claude", scraped_text)
            
        st.subheader("Summary:")
        st.write(summary)
