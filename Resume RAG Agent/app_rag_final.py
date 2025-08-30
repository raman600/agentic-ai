####################################################################################################################
# This code has resume extraction, job description analysis, ATS scoring, and improvement suggestions.
# It uses Autogen agents to process the resume and job description, score the resume, and provide improvement suggestions.
# The Streamlit UI allows users to upload a resume and enter a job description, then displays the results in a structured format.
# This has RAG implemented with Serper API for job search and connection to external databases.
####################################################################################################################

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import mammoth
import os
import PyPDF2 as pdf
import json
import re
import asyncio
import requests
import google.generativeai as genai
import chromadb
import hashlib
import pickle

from chromadb.utils import embedding_functions
from datetime import datetime
from autogen import AssistantAgent, UserProxyAgent
from typing import List, Dict, Any

from dotenv import load_dotenv

from rag import RAGKnowledgeBase
from db import SessionLocal, User, Resume, JobDescription, Score, get_user_resumes, get_user_job_descriptions, get_scores_for_resume
from setup import setup_agents
from process import extract_text_from_pdf, extract_text_from_docx, extract_text_from_file, process_resume, process_job_description
from score import score_resume, configure_scoring_agent_for_consistency
from feedback import improve_resume, display_section, save_resume, save_job_description, save_score, display_rag_insights, determine_top_skill, search_jobs_with_duckduckgo

load_dotenv() 

#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
api_key=os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")


#Streamlit UI
async def main():
    st.title("Resume Analyzer")

    if "knowledge_base" not in st.session_state:
        with st.spinner("Initializing AI Knowledge Base..."):
            st.session_state.knowledge_base = RAGKnowledgeBase()

    # Setup agents
    with st.spinner("Initializing agents..."):
        resume_agent, scoring_agent, job_agent, improvement_agent, coordinator = setup_agents()
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = 1  

    if "resume_processed" not in st.session_state:
        st.session_state.resume_processed = False
    if "resume_data" not in st.session_state:
        st.session_state.resume_data = {}
    if "score_data" not in st.session_state:
        st.session_state.score_data = {}
    if "improvement_data" not in st.session_state:
        st.session_state.improvement_data = {}

    user_id = st.session_state.user_id
    knowledge_base = st.session_state.knowledge_base
    
    st.text("Upload your resume in PDF format and provide the job description to analyze your resume.")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf", "docx", "txt"])
        
    jd_option = st.radio("How would you like to provide the Job Description?", ("Paste Text", "Upload File"))

    jd = None  
    jd_file = None

    if jd_option == "Paste Text":
        jd = st.text_area("Paste Job Description", height=200)

    elif jd_option == "Upload File":
        jd_file = st.file_uploader("Upload Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"], key="jd_file")
    
    if jd_file is not None:
        file_type = jd_file.type
        if file_type == "application/pdf":
            reader = pdf.PdfReader(jd_file)
            jd = "\n".join([page.extract_text() for page in reader.pages])
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            jd = mammoth.extract_raw_text(jd_file).value
        elif file_type == "text/plain":
            jd = jd_file.read().decode("utf-8")
        
    submit = st.button("Analyze my Resume")

    if submit:
            if uploaded_file is not None and jd:
                
                # Extract text from the resume
                if uploaded_file.type == "application/pdf":
                    resume_text = extract_text_from_pdf(uploaded_file)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    resume_text = extract_text_from_docx(uploaded_file)
                elif uploaded_file.type == "text/plain":
                    resume_text = extract_text_from_file(uploaded_file)
                else:
                    st.error("Unsupported file type. Please upload a PDF or DOCX file.")
                    return
                
                # Process the resume and job description
                resume_data = process_resume(resume_text, resume_agent, coordinator,knowledge_base)
                job_data = process_job_description(jd, job_agent, coordinator)
                
                # Score the resume
                scoring_agent = configure_scoring_agent_for_consistency(scoring_agent)
                score_data = score_resume(resume_data, job_data, scoring_agent, coordinator,knowledge_base)
                
                # Improve the resume
                improvement_data = improve_resume(resume_data, job_data, score_data, improvement_agent, coordinator,knowledge_base)
                
                # Store RAG insights in database
                rag_insights = knowledge_base.run_complete_rag_analysis(
                resume_text, jd, score_data.get("overall_score", 50), resume_data.get("Skills", [])
                )

                # Store in session state
                st.session_state.resume_data = resume_data
                st.session_state.score_data = score_data
                st.session_state.improvement_data = improvement_data
                st.session_state.rag_insights = rag_insights
                st.session_state.job_description = jd
                st.session_state.resume_processed = True

                # Save to database
                user_id = 1  
                resume_id = save_resume(user_id, uploaded_file, resume_text, resume_data)
                job_id = save_job_description(user_id, "JD Input", jd)
                score_id = save_score(resume_id, job_id, score_data)
            else:
                st.error("Please upload a resume and provide a job description.")

                # Store RAG insights
                knowledge_base.store_analysis_in_database(user_id, resume_id, job_id, 
                                                    score_data.get("score", 50), rag_insights)
        
    if st.session_state.resume_processed:
                # Display results
                display_section("ATS Score", st.session_state.score_data.get("overall_score", []))
                display_section("Feedback", st.session_state.score_data.get("feedback", []))
                display_section("Recommendations", st.session_state.score_data.get("recommendations", []))
                display_section("Format Improvements", st.session_state.improvement_data.get("format_improvements", []))
                display_section("Skill Gaps", st.session_state.improvement_data.get("skill_gaps", []))
                display_section("ATS Optimizations", st.session_state.improvement_data.get("ATS_optimizations", []))
                display_section("Actionable Steps", st.session_state.improvement_data.get("actionable_steps", []))
                display_section("Missing Keywords", st.session_state.improvement_data.get("missing_keywords", []))

                display_rag_insights(
                    st.session_state.knowledge_base,
                    st.session_state.resume_data, 
                    st.session_state.job_description
                )

                st.subheader("🌍 Search for Open Jobs Online")

                city = st.text_input("Enter your city (e.g., Auckland, New York, London)")
                if st.button("Find Jobs"):
                    if city:
                        resume_data = st.session_state.resume_data
                        if resume_data:
                            top_skill = determine_top_skill(resume_data, coordinator, resume_agent)
                            query = f"{top_skill} jobs in {city}"
                        else:
                            query = f"jobs in {city}"
                        
                        st.info(f"Searching jobs for: {query}")

                        jobs = search_jobs_with_duckduckgo(query)

                        if jobs:
                            for job in jobs:
                                st.markdown(f"### [{job['title']}]({job['link']})")
                                st.write(job['snippet'])
                                st.markdown("---")
                        else:
                            st.warning("No jobs found. Try a different city or role.")
                    else:
                        st.error("Please enter a city name.")
            
    user_id = st.session_state.get("user_id", 1)  # dummy until login
    
    st.header("Resume History")
    resumes = get_user_resumes(user_id)
    if resumes:
            resume_rows = []
            for res in resumes:
                scores = get_scores_for_resume(res.id)
                score_text = ", ".join([f"{sc.score} ({sc.created_at})" for sc in scores]) if scores else "No scores yet"

                resume_rows.append({
                    "Resume ID": res.id,
                    "File Name": res.file_name,
                    "Uploaded At": res.created_at,
                    "Scores": score_text
                })

            # Convert to DataFrame for display
            df_resumes = pd.DataFrame(resume_rows)

            # Show as interactive table
            st.dataframe(df_resumes.reset_index(drop=True), use_container_width=True, hide_index=True)
    else:
            st.info("No resumes found in history.")
  

if __name__ == "__main__":
   asyncio.run(main())

