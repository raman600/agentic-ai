import json
import streamlit as st
import re
from typing import Dict, Any
from rag import RAGKnowledgeBase
from process import normalize_data, create_content_hash, get_cached_score, cache_score

# Function to score resume with consistent methodology
def score_resume(resume_data: Dict[str, Any], job_data: Dict[str, Any], scoring_agent, coordinator, knowledge_base: RAGKnowledgeBase) -> Dict[str, Any]:
    """Score the resume against the job description with consistency."""
    
    normalized_resume = normalize_data(resume_data)
    normalized_job = normalize_data(job_data)
    #st.write("Hash input string:", f"{json.dumps(normalized_resume, sort_keys=True)}|{json.dumps(normalized_job, sort_keys=True)}")

    content_hash = create_content_hash(resume_data, job_data)
    #st.write("Content hash for caching:", content_hash)

    cached_score = get_cached_score(content_hash)
    """if cached_score:
            st.write("Cache hit!")
            st.write(cached_score)
            st.success("✅ Retrieved cached score (consistent result)")
            return cached_score
    else:
            st.write("Cache miss. Computing score.")"""
        
 
    
    # EXTRACT SKILLS WITH CONSISTENT PROCESSING
    resume_skills = normalized_resume.get("Skills", []) if isinstance(normalized_resume, dict) else []
    job_description = json.dumps(normalized_job, sort_keys=True, ensure_ascii=True)  # Consistent string representation
    resume_description = json.dumps(normalized_resume, sort_keys=True, ensure_ascii=True)

    # GET RAG CONTEXT WITH DETERMINISTIC ORDERING
    industry_insights = knowledge_base.get_intelligent_industry_insights(job_description, resume_description)
    skill_analysis = knowledge_base.get_intelligent_skill_matching(resume_skills, job_description)
    
    # CALCULATE DETERMINISTIC PRELIMINARY SCORE
    job_text = json.dumps(normalized_job, sort_keys=True) if isinstance(normalized_job, dict) else str(normalized_job)
    resume_text = json.dumps(normalized_resume, sort_keys=True) if isinstance(normalized_resume, dict) else str(normalized_resume)
        
    job_keywords = set(word.lower().strip() for word in job_text.split() if len(word) > 3 and word.isalpha())
    resume_keywords = set(word.lower().strip() for word in resume_text.split() if len(word) > 3 and word.isalpha())
    keyword_overlap = len(job_keywords & resume_keywords)
    
    # More sophisticated scoring
    preliminary_score = min(100, (keyword_overlap / max(len(job_keywords), 1)) * 100)
    
    historical_insights = knowledge_base.get_historical_scoring_insights(
        preliminary_score, 
        resume_description, 
        job_description
    )
    
    # CREATE DETERMINISTIC PROMPT
    structured_prompt = f"""
    RAG CONTEXT (DETERMINISTIC ANALYSIS):
    
    INDUSTRY ANALYSIS:
    {industry_insights}
    
    SKILL MATCHING ANALYSIS:
    {skill_analysis}
    
    HISTORICAL SCORING PATTERNS:
    {historical_insights}
    
    SCORING TASK:
    Please score the following resume against the job description.
    Provide consistent, objective scoring based on:
    - Exact keyword matches
    - Required skills alignment
    - Experience relevance
    - Education requirements
    
    RESUME DATA: {resume_description}
    
    JOB DATA: {job_description}
    
    IMPORTANT: Provide scoring in this exact JSON format with consistent methodology:
    {{
        "overall_score": <integer 0-100>,
        "keyword_match": <integer 0-100>,
        "skills_match": <integer 0-100>,
        "experience_match": <integer 0-100>,
        "education_match": <integer 0-100>,
        "recommendations": ["<specific improvement 1>", "<specific improvement 2>"]
    }}
    """
    
    # CONFIGURE LLM FOR CONSISTENCY
    
    response = coordinator.initiate_chat(
        scoring_agent,
        message=structured_prompt,
        max_turns=1,
        #temperature=0.0,  # For deterministic output
        #seed=42,  # Fixed seed
        #top_p=0.1  # Low top_p for consistency
    )
    
    response_text = response.chat_history[-1]['content']
    
    # PARSE AND VALIDATE RESPONSE
    try:
        # Try to extract JSON from response if it's wrapped in other text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group()
        else:
            json_text = response_text

        json_data = json.loads(json_text)
        
        # Ensure all required fields exist with default values
        required_fields = {
            "overall_score": 0,
            "keyword_match": 0,
            "skills_match": 0,
            "experience_match": 0,
            "education_match": 0,
            "recommendations": []
        }
        
        for field, default in required_fields.items():
            if field not in json_data:
                json_data[field] = default
        
        # Round scores to avoid floating point variations
        for score_field in ["overall_score", "keyword_match", "skills_match", "experience_match", "education_match"]:
            if isinstance(json_data[score_field], (int, float)):
                json_data[score_field] = round(json_data[score_field])
        
        # Ensure recommendations is a list
        if not isinstance(json_data["recommendations"], list):
            json_data["recommendations"] = [str(json_data["recommendations"])]
        
    except (json.JSONDecodeError, AttributeError) as e:
        st.warning(f"Could not parse LLM response as JSON: {e}")
        # Fallback scoring if JSON parsing fails
        json_data = {
            "overall_score": int(preliminary_score),
            "keyword_match": int(preliminary_score * 0.8),
            "skills_match": int(preliminary_score * 0.9),
            "experience_match": int(preliminary_score * 0.7),
            "education_match": int(preliminary_score * 0.6),
            "recommendations": ["Unable to parse detailed analysis"]
        }
    
    # 10. CACHE THE RESULT
    cache_score(content_hash, json_data)
    
    st.success("✅ Successfully scored resume")
    return json_data

def configure_scoring_agent_for_consistency(scoring_agent):
    """Configure the scoring agent for deterministic responses"""
    
    # Ensure LLM config exists
    if hasattr(scoring_agent, 'llm_config') and scoring_agent.llm_config is not None:
        try:
            # Set individual attributes for Pydantic models
            scoring_agent.llm_config.temperature = 0.0
            scoring_agent.llm_config.seed = 42
            
            # Try to set other parameters if they exist
            if hasattr(scoring_agent.llm_config, 'top_p'):
                scoring_agent.llm_config.top_p = 0.1
            if hasattr(scoring_agent.llm_config, 'frequency_penalty'):
                scoring_agent.llm_config.frequency_penalty = 0
            if hasattr(scoring_agent.llm_config, 'presence_penalty'):
                scoring_agent.llm_config.presence_penalty = 0
            if hasattr(scoring_agent.llm_config, 'max_tokens'):
                scoring_agent.llm_config.max_tokens = 1000
                
        except AttributeError as e:
            # If direct attribute setting fails, try alternative approaches
            st.warning(f"Could not configure all LLM parameters: {e}")
            
            # Try setting as dictionary if it supports item assignment
            try:
                scoring_agent.llm_config["temperature"] = 0.0
                scoring_agent.llm_config["seed"] = 42
            except (TypeError, KeyError):
                pass
    
    return scoring_agent
