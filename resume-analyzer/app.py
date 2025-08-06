import streamlit as st
import os
import google.generativeai as genai
import PyPDF2 as pdf
import json
import re

from dotenv import load_dotenv

load_dotenv() 

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#Get response from Gemini model
def get_gemini_response(input):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(input)
    return response.text

#Convert PDF to text
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

#Display results in human readable format
def display_results(result):
    """Display the results in a human-readable format."""

    st.header("Analysis Results")

    # Match percentage
    match_score = result.get("resume_matching_percentage", [])
    if isinstance(match_score, str):
        match_score_cleaned = re.sub(r'[^\d]', '', match_score)
    try:
        match_score = int(match_score_cleaned)
    except ValueError:
        match_score = None

    match_str = f"{match_score}%" if match_score is not None else "N/A"
    
    col1, col2 = st.columns([1, 3])

    with col1:
        st.metric("Job Description Match", match_str)
    
    with col2:
        try:
            match_num = int(match_score)
            st.progress(match_num/100)
            
            if match_num > 80:
                st.success("Your resume is a strong match for the job description!")
            elif match_num > 50:
                st.warning("Your resume is a moderate match. Consider improving it.")
            else:
                st.error("Your resume is a weak match. Significant improvements are needed.")
        except:
            st.info("Invalid match percentage format.")
    
    st.divider()

    # Missing keywords
    st.header("Missing Keywords")

    missing_keywords = result.get("missing_keywords", [])

    if missing_keywords:
        st.write ("The following important keywords are missing from your resume:")
        
        cols = st.columns(3)
        for i, keyword in enumerate(missing_keywords):
            with cols[i % 3]:
                st.write(f"- {keyword}")
    else:
        st.success("No important keywords are missing from your resume!")

    st.divider()

    # Profile summary
    st.header("Profile Summary")
    feedback = result.get("feedback", [])  

    # If "feedback" is a string instead of a list
    if isinstance(feedback, str):
        feedback = [feedback]

    if feedback:
        for sentence in feedback:
            st.write(f"- {sentence}")
    else:
        st.info("No feedback provided in the analysis.")

    st.divider()

input_prompt = """

Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of tech job market, including software engineering, data science, data analyst
and big data engineer roles. Your task is to evaluate the resume based on the given job description.
Consider the job market to be very competitive so you should provide the
best assistance for improving the resume. Assign percentage matching based
on Job description (JD) and the missing keywords with high accuracy.  

resume:{text}  
description:{jd}  


Only respond with valid JSON, using the following keys:
- "resume_matching_percentage" (percentage, like "80%")
- "missing_keywords" (list of keywords missing from the resume)
- "feedback" (summary of the resume for the job)

  Do not include any explanation or extra text.

""" 

#Streamlit UI
st.title("Resume Analyzer")
st.text("Upload your resume in PDF format and provide the job description to analyze your resume.")
jd = st.text_area("Job Description", height=200)
uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

submit = st.button("Analyze my Resume")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        prompt = input_prompt.format(text=text, jd=jd)
        response = get_gemini_response(prompt)
        # Extract JSON object from response using regex
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                result = json.loads(json_str)
                display_results(result)
            except json.JSONDecodeError as e:
                st.error("Could not parse the JSON. Here's the error:")
                st.write(str(e))
                st.write("Raw JSON:")
                st.code(json_str, language="json")
        else:
            st.error("No valid JSON response found in the output.")
            st.write(response)