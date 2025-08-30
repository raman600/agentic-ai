import json
import requests
import streamlit as st
from datetime import datetime
from typing import Dict, Any
from rag import RAGKnowledgeBase
from db import SessionLocal, User, Resume, JobDescription, Score, get_user_resumes, get_user_job_descriptions, get_scores_for_resume

def improve_resume(resume_data: Dict[str, Any], job_data: Dict[str, Any], score_data: Dict[str, Any], improvement_agent, coordinator, knowledge_base: RAGKnowledgeBase) -> Dict[str, Any]:
    """Provide suggestions to improve the resume based on the job description and score."""
    prompt = f"Suggest improvements for the resume data: {resume_data} based on job description: {job_data} and score: {score_data}"
    response = coordinator.initiate_chat(
        improvement_agent,
        message=prompt,
        max_turns=1
    )
    response_text = response.chat_history[-1]['content']
    json_data = json.loads(response_text)
    #st.json(json_data)
    st.success("✅ Successfully improved resume")
    return json_data

def store_user_feedback(knowledge_base: RAGKnowledgeBase, resume_data: Dict, score_data: Dict, user_feedback: str):
    """Store user feedback to improve the knowledge base"""
    try:
        feedback_data = {
            "id": f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "score": score_data.get("score", 0),
            "feedback": user_feedback,
            "resume_skills": resume_data.get("Skills", []),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to patterns collection for future learning
        knowledge_base.patterns_collection.add(
            documents=[f"User feedback: {user_feedback}"],
            metadatas=[feedback_data],
            ids=[feedback_data["id"]]
        )
        st.success("Thank you for your feedback! It will help improve future recommendations.")
    except Exception as e:
        st.error(f"Error storing feedback: {e}")

def display_section(title, data):
    st.subheader(title)

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                # Handle nested dictionaries (like experience)
                for k, v in item.items():
                    st.markdown(f"**{k}:** {v}" if not isinstance(v, list) else "")
                    if isinstance(v, list):
                        for sub_item in v:
                            st.markdown(f"- {sub_item}")
            else:
                st.markdown(f"- {item}")
    elif isinstance(data, dict):
        for key, value in data.items():
            st.markdown(f"**{key}:** {value}")
    else:
        st.markdown(str(data))

#Save the resume, job description and score to the database

def save_resume(user_id, uploaded_file, resume_text, resume_data):
    session = SessionLocal()
    resume = Resume(
        user_id=user_id,
        file_name=uploaded_file.name,
        raw_text=resume_text,
        extracted_json=json.dumps(resume_data)
    )
    session.add(resume)
    session.commit()
    return resume.id

def save_job_description(user_id, jd_title, jd_text):
    session = SessionLocal()
    jd = JobDescription(user_id=user_id, title=jd_title, description=jd_text)
    session.add(jd)
    session.commit()
    return jd.id

def save_score(resume_id, job_id, score_data):
    session = SessionLocal()
    score = Score(
        resume_id=resume_id,
        job_id=job_id,
        score=score_data["overall_score"],
        feedback=json.dumps(score_data.get("feedback", {})),
        recommendations=json.dumps(score_data.get("recommendations", {}))
    )
    session.add(score)
    session.commit()
    return score.id


def search_jobs_with_serper(query: str):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "q": query,
        "num": 5   # number of results
    })

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        return []

    data = response.json()
    jobs = []

    # Parse search results
    for item in data.get("organic", []):
        jobs.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })
    return jobs

def search_jobs_with_duckduckgo(query: str):
    url = "https://api.duckduckgo.com/"
    
    params = {
        "q": query,
        "format": "json",
        "no_html": "1",
        "skip_disambig": "1"
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        jobs = []
        
        # Parse results from different DuckDuckGo result types
        # Related topics often contain the most useful results
        for item in data.get("RelatedTopics", []):
            if isinstance(item, dict) and "Text" in item and "FirstURL" in item:
                jobs.append({
                    "title": item.get("Text", "").split(" - ")[0] if " - " in item.get("Text", "") else item.get("Text", ""),
                    "link": item.get("FirstURL"),
                    "snippet": item.get("Text", "")
                })
        
        # If no related topics, try the main result
        if not jobs and data.get("Abstract"):
            jobs.append({
                "title": data.get("Heading", query),
                "link": data.get("AbstractURL", ""),
                "snippet": data.get("Abstract", "")
            })
        
        return jobs[:5]  # 5 results
        
    except Exception as e:
        print(f"Error searching DuckDuckGo: {e}")
        return []

def determine_top_skill(resume_data, coordinator, resume_agent):
    """Ask the LLM to determine the candidate's strongest skill."""
    prompt = f"""
    Analyze this resume data: {resume_data}.
    Identify the ONE skill or domain the candidate is most highly skilled in.
    Return only the skill name, nothing else.
    """
    response = coordinator.initiate_chat(
        resume_agent,
        message=prompt,
        max_turns=1
    )
    return response.chat_history[-1]['content'].strip()

def display_rag_insights(knowledge_base: RAGKnowledgeBase, resume_data: Dict, job_description: str):
    """Display comprehensive RAG insights."""
    
    st.header("AI Knowledge Base Insights")
    
    resume_skills = resume_data.get("Skills", [])
    resume_text = str(resume_data)
    
    # Get all RAG insights
    with st.spinner("Generating intelligent insights..."):
        rag_results = knowledge_base.run_complete_rag_analysis(
            resume_text, job_description, 
            st.session_state.score_data.get("score", 50), 
            resume_skills
        )
    
    # Display in expandable sections
    with st.expander("🏭 Industry Intelligence", expanded=True):
        st.write(rag_results['industry_insights'])
    
    with st.expander("⚡ Optimization Recommendations"):
        st.write(rag_results['optimization_recommendations'])
    
    with st.expander("🎯 Advanced Skill Analysis"):
        st.write(rag_results['skill_matching'])
    
    #with st.expander("📊 Historical Performance Insights"):
        #st.write(rag_results['scoring_insights'])
