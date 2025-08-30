import streamlit as st
import PyPDF2 as pdf
import mammoth
import json
from typing import Dict, Any
import pickle
import hashlib
from rag import RAGKnowledgeBase

#Convert documents to text
def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from a PDF file."""
    reader = pdf.PdfReader(uploaded_file)
    st.success("✅ Extracting text from resume")
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

def extract_text_from_docx(uploaded_file) -> str:
    """Extract text from a DOCX file."""
    result = mammoth.extract_raw_text(uploaded_file)
    return result.value

def extract_text_from_file(uploaded_file) -> str:
    """Extract from plain text file."""
    if uploaded_file.type == "text/plain":
        return str(uploaded_file.read(), "utf-8")

#Process the resume and job description, generate ATS score    

def process_resume(resume_text: str, resume_agent, coordinator, knowledge_base: RAGKnowledgeBase) -> Dict[str, Any]:
    """Process resume using Autogen agents."""
    
    optimization_context = knowledge_base.get_resume_optimization_recommendations(resume_text)

    prompt = f""" RAG CONTEXT - Resume Best Practices: 
    {optimization_context} 
    Extract structured data from the resume text: {resume_text} 
    Use the above context to identify any formatting or structural issues.
    """
    response = coordinator.initiate_chat(
        resume_agent,
        message=prompt,
        max_turns=1
    )
    response_text = response.chat_history[-1]['content']
    json_data = json.loads(response_text)
    #st.json(json_data)
    st.success("✅ Processed resume")
    return json_data

def process_job_description(jd_text: str, job_agent, coordinator) -> Dict[str, Any]:
    """Process job description using Autogen agents."""
    prompt = f"Extract key skills and requirements from the job description: {jd_text}"
    response = coordinator.initiate_chat(
        job_agent,
        message=prompt,
        max_turns=1
    )
    response_text = response.chat_history[-1]['content']
    json_data = json.loads(response_text)
    #st.json(json_data)
    st.success("✅ Processed job description")
    return json_data

# CACHING FUNCTIONS FOR CONSISTENCY IN SCORES
def get_cached_score(content_hash: str) -> Dict[str, Any]:
    """Retrieve cached score if exists"""
    try:
        with open(f"score_cache_{content_hash}.pkl", "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, pickle.PickleError):
        return None

def cache_score(content_hash: str, score_data: Dict[str, Any]):
    """Cache the score for future consistency"""
    try:
        with open(f"score_cache_{content_hash}.pkl", "wb") as f:
            pickle.dump(score_data, f)
    except Exception as e:
        print(f"Warning: Could not cache score: {e}")

    # NORMALIZE AND STANDARDIZE INPUT DATA
def normalize_data(data):
        """Ensure consistent data format with deep normalization"""
        if isinstance(data, dict):
            # Sort keys and normalize values recursively
            normalized = {}
            for key, value in sorted(data.items()):
                if isinstance(value, list):
                    # Sort lists and normalize strings, handle nested structures
                    normalized_list = []
                    for item in value:
                        if isinstance(item, str):
                            normalized_list.append(item.strip().lower())
                        elif isinstance(item, dict):
                            normalized_list.append(normalize_data(item))
                        else:
                            normalized_list.append(item)
                    # Sort the list for consistency
                    try:
                        normalized[key] = sorted(normalized_list)
                    except TypeError:
                        # If items aren't sortable, keep original order but normalized
                        normalized[key] = normalized_list
                elif isinstance(value, str):
                    normalized[key] = value.strip().lower()
                elif isinstance(value, dict):
                    normalized[key] = normalize_data(value)
                elif isinstance(value, (int, float)):
                    normalized[key] = value
                else:
                    # Convert to string and normalize for other types
                    normalized[key] = str(value).strip().lower()
            return normalized
        elif isinstance(data, list):
            normalized_list = []
            for item in data:
                if isinstance(item, str):
                    normalized_list.append(item.strip().lower())
                elif isinstance(item, dict):
                    normalized_list.append(normalize_data(item))
                else:
                    normalized_list.append(item)
            try:
                return sorted(normalized_list)
            except TypeError:
                return normalized_list
        elif isinstance(data, str):
            return data.strip().lower()
        else:
            return data

  # CREATE DETERMINISTIC HASH FOR CACHING
def create_content_hash(resume_data, job_data):
    normalized_resume = normalize_data(resume_data)
    normalized_job = normalize_data(job_data)

        # Create a consistent string representation
    resume_str = json.dumps(normalized_resume, sort_keys=True)
    job_str = json.dumps(normalized_job, sort_keys=True)
    combined = f"{resume_str}|{job_str}"
    return hashlib.sha256(combined.encode()).hexdigest()
