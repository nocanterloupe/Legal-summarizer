import streamlit as st
from transformers import pipeline
import pdfplumber
import docx2txt
import tempfile

# Load your fine-tuned summarization model
# Replace 'your-fine-tuned-model-name' with your real model name (if uploaded to Hugging Face)
summarizer = pipeline("summarization", model="your-fine-tuned-model-name")

# Extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

# Extract text from DOCX
def extract_text_from_docx(file):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    temp_file.write(file.read())
    temp_file.close()
    text = docx2txt.process(temp_file.name)
    return text

# Main Streamlit App
def main():
    st.set_page_config(page_title="Legal Document Summarizer", layout="wide")
    st.title("📚 Legal Document Summarizer for Lawyers")

    st.write("Upload a legal document (PDF, DOCX, or TXT) to get a smart and accurate summary.")

    uploaded_file = st.file_uploader("Choose a legal file to summarize", type=["pdf", "docx", "txt"])

    summary_length = st.selectbox(
        "Select summary length",
        ("Short", "Medium", "Long")
    )

    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(uploaded_file)
        else:
            text = uploaded_file.read().decode('utf-8')

        if text:
            st.subheader("📄 Extracted Text")
            st.text_area("Full Text", text, height=300)

            if st.button("🧠 Summarize Document"):
                if summary_length == "Short":
                    max_length = 100
                    min_length = 30
                elif summary_length == "Medium":
                    max_length = 300
                    min_length = 100
                else:
                    max_length = 500
                    min_length = 250

                with st.spinner("Summarizing, please wait..."):
                    summary = summarizer(
                        text,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=False
                    )
                    summarized_text = summary[0]['summary_text']

                st.success("✅ Summary Generated Successfully!")
                st.subheader("📝 Summarized Text")
                st.text_area("Summary", summarized_text, height=300)

                # Download Summary Button
                st.download_button(
                    label="📥 Download Summary",
                    data=summarized_text,
                    file_name="legal_summary.txt",
                    mime="text/plain"
                )
        else:
            st.warning("⚠️ No text could be extracted from this document. Please try another file.")

if __name__ == "__main__":
    main()
