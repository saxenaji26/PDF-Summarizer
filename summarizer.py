import streamlit as st
from transformers import pipeline
import pdfplumber
import re

def extract_text_from_pdf(pdf_file_path):
    text = ""
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def clean_text(text):
    # Replace common problematic characters like '(cid:415)' with 'ti'
    text = re.sub(r'\(cid:\d+\)', 'ti', text)  # Replace '(cid:###)' with 'ti'
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    return text

def summarize_pdf(pdf_file_path, max_length=150, min_length=50):
    text = extract_text_from_pdf(pdf_file_path)
    text = clean_text(text)
    summarizer = pipeline("summarization", "sshleifer/distilbart-cnn-12-6")
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

st.title("PDF Summarizer")
pdf_file = st.file_uploader("Drop your PDF file here but it should contain up to 3 pages", type=["pdf"])

if pdf_file is not None:
    pdf_file_path = pdf_file.name
    with open(pdf_file_path, "wb") as f:
        f.write(pdf_file.read())

    summary = summarize_pdf(pdf_file_path)

    st.subheader("Summary")
    edited_summary = st.text_area("Edit the summary if needed:", summary, height=200)

    if st.button("Save Summary"):
        # Create a downloadable text file
        with open("summary.txt", "w") as file:
            file.write(edited_summary)

        with open("summary.txt", "rb") as file:
            btn = st.download_button(
                label="Download Summary",
                data=file,
                file_name="summary.txt",
                mime="text/plain"
            )
