import streamlit as st
import os
from dotenv import load_dotenv
from resume_parser import extract_resume_text
from jd_matcher import match_resume_to_jd
from keyword_analyzer import missing_keywords
from score_generator import generate_score
from ai_suggester import get_resume_suggestions
from resume_rewriter import rewrite_resume

# Load environment variables from .env file
load_dotenv()

# Page config (must be the first Streamlit command)
st.set_page_config(
    page_title="Advanced Resume Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UI ELEMENTS ---
st.title("📄 Advanced Resume Optimizer")

# Job Description
st.header("Job Description")
jd_text = st.text_area("Paste the Job Description here:", height=200)

# Resume Upload
st.header("Upload Your Resume")
uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])

# --- PROCESSING AND DISPLAY ---
if st.button("Analyze Resume"):
    if uploaded_file is not None and jd_text:
        with st.spinner("Analyzing..."):
            # Save the uploaded file temporarily
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Extract text from resume
            resume_text = extract_resume_text(uploaded_file.name)

            if resume_text:
                # --- CALCULATIONS ---
                similarity_score = match_resume_to_jd(resume_text, jd_text)
                missing = missing_keywords(resume_text, jd_text)
                final_score = generate_score(similarity_score, missing)
                suggestions = get_resume_suggestions(resume_text, jd_text)
                rewritten_resume = rewrite_resume(resume_text, jd_text)


                # --- DISPLAY RESULTS ---
                st.header("Analysis Results")
                st.subheader(f"Overall Match Score: {final_score}%")
                st.progress(int(final_score))


                st.subheader(f"Semantic Similarity with Job Description: {similarity_score}%")


                st.subheader("Keywords Missing from Your Resume:")
                st.info(", ".join(missing))


                st.subheader("AI-Powered Suggestions:")
                st.markdown(suggestions)


                st.subheader("Rewritten Resume Summary:")
                st.markdown(rewritten_resume)

            else:
                st.error("Could not extract text from the resume. Please try another file.")

            # Clean up the temporary file
            os.remove(uploaded_file.name)
    else:
        st.warning("Please upload a resume and paste the job description.")