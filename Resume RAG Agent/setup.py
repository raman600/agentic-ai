from autogen import AssistantAgent, UserProxyAgent
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv() 
api_key=os.getenv("OPENAI_API_KEY")

config_list = [
    {
        "model": "gpt-4o",
        "api_key": api_key,
        "api_type": "openai",
       
    }
]

def setup_agents():
    """Setup the user and assistant agents for the resume analysis."""
    
    resume_agent = AssistantAgent(
        name="ResumeAgent",
        system_message="You are an advanced resume analysis agent with access to industry knowledge and best practices.  \
            Use the provided RAG context including industry insights and best practices to enhance your analysis. \
            Extract data from resume and return structured JSON with: \
            1. Name 2. Email 3. Phone Number 4. Skills 5. Education 6. Experience\
            7. Certifications 8. Summary 9. Languages 10. Projects 11. Publications\" \
                Use the provided industry insights and best practices to enhance your analysis. \
                    Be thorough and return all relevant information.\
                        IMPORTANT: Return ONLY the JSON object, no explanations, no markdown, no code blocks.",
        llm_config={"config_list": config_list},
        human_input_mode="NEVER"
    )

    scoring_agent = AssistantAgent(
        name="ScoringAgent",
        system_message="You are an ATS scoring agent. \
            Analyze the resume data against the job description and return a score from 0 to 100. \" \
            Use the provided RAG context including:\
                - Industry-specific requirements \
                - Historical scoring patterns \
                - Best practices for optimization \
            Provide a detailed explanation of the score considering the retrieved context. \
            Use skills, experience, achievements and education to determine the score.\
            Return a JSON with 'score', 'feedback' and 'recommendations'.\
                IMPORTANT: Return ONLY the JSON object, no explanations, no markdown, no code blocks.",
        llm_config={"config_list": config_list},
        human_input_mode="NEVER"
    )

    job_agent = AssistantAgent(
        name="JobDescriptionAgent",
        system_message="You are a job description analysis agent. \
            Extract key skills, qualifications and requirements from the job description. \
            Return a structured JSON with 'skills', 'qualifications' and 'requirements'.\
                IMPORTANT: Return ONLY the JSON object, no explanations, no markdown, no code blocks.",
        llm_config={"config_list": config_list},
        human_input_mode="NEVER"
    )

    improvement_agent = AssistantAgent(
        name="ImprovementAgent",
        system_message="You are an improvement agent  with access to best practices and skill insights. \
            Analyze the resume and job description to provide suggestions for improvement. \" \
            Use the provided context including: \
                - Best practices for resume optimization \
                - Skill taxonomy and related skills \
                - Industry-specific insights \
                - Historical improvement patterns \
            Return a JSON with missing keywords, format improvements, skill gaps, ATS optimizations and actionable_steps.\
                IMPORTANT: Return ONLY the JSON object, no explanations, no markdown, no code blocks.",
        llm_config={"config_list": config_list},
        human_input_mode="NEVER"
    )

    coordinator = UserProxyAgent(
        name="Coordinator",
        system_message="You are the RAG-enhanced coordinator agent. \
            Manage the flow of information between the user, resume agent, scoring agent and job description agent and incorporate retrieved knowledge. \
            Ensure all agents have the necessary data to perform their tasks.",
        llm_config={"config_list": config_list},
        human_input_mode="NEVER"
    )
    
    return resume_agent, scoring_agent, job_agent, improvement_agent, coordinator
