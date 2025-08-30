import chromadb
import streamlit as st
import os
import google.generativeai as genai
import openai

from dotenv import load_dotenv
from typing import List, Dict, Any
from datetime import datetime
from chromadb.utils import embedding_functions

load_dotenv()
#api_key=os.getenv("GOOGLE_API_KEY")
api_key=os.getenv("OPENAI_API_KEY")

class RAGKnowledgeBase:
    """RAG-Enhanced Knowledge Base for Resume Analysis Integration"""
    
    def __init__(self):
        self.client = chromadb.Client()
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-ada-002"
        )
        # Initialize GoogleAI for generation
        #genai.configure(api_key=api_key)
        #self.llm = genai.GenerativeModel('gemini-2.5-flash')
        
        # Initialize OpenAI
        self.llm = openai
        self.initialize_collections()
        self.populate_knowledge_base()

    def _process_metadata(self, metadata: Dict) -> Dict:
        """Convert lists in metadata to comma-separated strings"""
        processed = {}
        for key, value in metadata.items():
            if isinstance(value, list):
                processed[key] = ", ".join(str(item) for item in value)
            else:
                processed[key] = value
        return processed

    def _generate_llm_response_gemini(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response using Gemini's LLM"""
        try:
            generation_config = {
                "temperature": 0.3,
                "max_output_tokens": max_tokens,
            }
            
            response = self.llm.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text.strip()
        
        except Exception as e:
            st.error(f"Error generating LLM response: {e}")
            return "Error generating intelligent insights. Using basic analysis." 
    
    def _generate_llm_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response using OpenAI's API"""
        try:
            response = self.llm.chat.completions.create(
                model="gpt-4o-mini",  
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,  
                max_tokens=max_tokens,
                # For consistency 
                seed=42,  
                top_p=0.1  
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating OpenAI response: {e}")
            return ""

    def initialize_collections(self):
        """Initialize ChromaDB collections for RAG knowledge base"""
        try:
            self.industry_collection = self.client.create_collection(
                name="industry_requirements",
                embedding_function=self.embedding_function
            )
            
            self.best_practices_collection = self.client.create_collection(
                name="best_practices",
                embedding_function=self.embedding_function
            )
            
            self.skills_collection = self.client.create_collection(
                name="skills_taxonomy",
                embedding_function=self.embedding_function
            )
            
            self.patterns_collection = self.client.create_collection(
                name="historical_patterns",
                embedding_function=self.embedding_function
            )
            
        except Exception:
            # Collections might already exist
            self.industry_collection = self.client.get_collection("industry_requirements")
            self.best_practices_collection = self.client.get_collection("best_practices")
            self.skills_collection = self.client.get_collection("skills_taxonomy")
            self.patterns_collection = self.client.get_collection("historical_patterns")

    def populate_knowledge_base(self):
        """Populate knowledge base with comprehensive data"""
        
        # Expanded industry-specific requirements
        industry_data = [
            {
                "id": "tech_req_1",
                "industry": "Technology",
                "requirements": "Strong programming skills in Python, Java, or JavaScript. Experience with cloud platforms (AWS, Azure, GCP). Understanding of software development lifecycle. Version control with Git. Problem-solving and analytical thinking. Agile/Scrum methodologies.",
                "key_skills": ["Python", "Java", "JavaScript", "AWS", "Azure", "GCP", "Git", "SDLC", "Agile", "Scrum"],
                "experience_level": "mid-level",
                "salary_range": "70000-120000",
                "growth_trend": "high"
            },
            {
                "id": "finance_req_1", 
                "industry": "Finance",
                "requirements": "Strong analytical and quantitative skills. Proficiency in Excel, SQL, and financial modeling. Knowledge of financial regulations. Risk management experience. CFA or FRM certifications preferred. Bloomberg terminal experience.",
                "key_skills": ["Excel", "SQL", "Financial Modeling", "Risk Management", "CFA", "FRM", "Bloomberg", "VBA"],
                "experience_level": "senior",
                "salary_range": "80000-150000",
                "growth_trend": "stable"
            },
            {
                "id": "marketing_req_1",
                "industry": "Marketing",
                "requirements": "Digital marketing expertise including SEO, SEM, social media marketing. Analytics tools like Google Analytics, Facebook Ads Manager. Content creation and campaign management. Marketing automation tools like HubSpot, Marketo.",
                "key_skills": ["SEO", "SEM", "Social Media", "Google Analytics", "Content Marketing", "HubSpot", "Marketo"],
                "experience_level": "entry-level",
                "salary_range": "45000-80000",
                "growth_trend": "high"
            },
            {
                "id": "healthcare_req_1",
                "industry": "Healthcare",
                "requirements": "Clinical experience with patient care. Knowledge of medical terminology and procedures. EMR/EHR systems proficiency. HIPAA compliance understanding. Strong communication skills for patient interaction.",
                "key_skills": ["Patient Care", "Medical Terminology", "EMR", "EHR", "HIPAA", "Clinical Skills"],
                "experience_level": "entry-level",
                "salary_range": "50000-90000",
                "growth_trend": "high"
            }
        ]
        
        # Comprehensive best practices
        best_practices_data = [
            {
                "id": "format_bp_1",
                "category": "Formatting",
                "practice": "Use consistent formatting with clear section headers. Maintain 1-inch margins and use a professional font like Arial or Calibri. Keep resume to 1-2 pages maximum. Use bullet points for easy scanning.",
                "importance": "high",
                "ats_impact": "Improves ATS parsing accuracy by 40%",
                "success_rate": "85%"
            },
            {
                "id": "keywords_bp_1",
                "category": "Keywords",
                "practice": "Include industry-specific keywords and action verbs. Mirror language from job descriptions. Use both acronyms and full forms of technical terms. Include skill variations and synonyms.",
                "importance": "critical",
                "ats_impact": "Increases match rate by 60%",
                "success_rate": "92%"
            },
            {
                "id": "quantify_bp_1",
                "category": "Achievements",
                "practice": "Quantify achievements with specific numbers, percentages, and metrics. Use action verbs to start bullet points. Focus on results and impact rather than responsibilities. Include before/after comparisons.",
                "importance": "high",
                "ats_impact": "Improves relevance scoring by 35%",
                "success_rate": "78%"
            },
            {
                "id": "ats_bp_1",
                "category": "ATS Optimization",
                "practice": "Avoid headers/footers, graphics, tables, and unusual fonts. Use standard section names (Experience, Education, Skills). Save as .docx or .pdf. Include both hard and soft skills sections.",
                "importance": "critical",
                "ats_impact": "Prevents automatic rejection by 70%",
                "success_rate": "95%"
            }
        ]
        
        # Detailed skills taxonomy
        skills_data = [
            {
                "id": "skill_python",
                "skill": "Python",
                "category": "Programming Language",
                "related_skills": ["Django", "Flask", "Pandas", "NumPy", "Machine Learning", "Data Science"],
                "industry_relevance": ["Technology", "Data Science", "Finance", "Healthcare"],
                "proficiency_indicators": ["years of experience", "projects completed", "certifications", "GitHub contributions"],
                "demand_level": "high",
                "salary_impact": "15-25%"
            },
            {
                "id": "skill_sql",
                "skill": "SQL",
                "category": "Database",
                "related_skills": ["MySQL", "PostgreSQL", "Data Analysis", "Database Design", "ETL", "Data Warehousing"],
                "industry_relevance": ["Technology", "Finance", "Healthcare", "Marketing"],
                "proficiency_indicators": ["query complexity", "database size", "optimization experience", "certifications"],
                "demand_level": "very_high",
                "salary_impact": "10-20%"
            },
            {
                "id": "skill_aws",
                "skill": "AWS",
                "category": "Cloud Platform",
                "related_skills": ["EC2", "S3", "Lambda", "RDS", "CloudFormation", "DevOps"],
                "industry_relevance": ["Technology", "Startups", "Enterprise"],
                "proficiency_indicators": ["certifications", "services used", "architecture experience"],
                "demand_level": "very_high",
                "salary_impact": "20-30%"
            }
        ]
        
        # Historical scoring patterns with more data
        patterns_data = [
            {
                "id": "pattern_tech_high",
                "score_range": "85-95",
                "common_factors": "Strong technical skills match, quantified project outcomes, relevant certifications, open-source contributions, modern tech stack alignment",
                "industry": "Technology",
                "improvement_suggestions": "Add leadership examples, include system design experience, mention team collaboration",
                "sample_size": "150+ resumes",
                "success_rate": "94%"
            },
            {
                "id": "pattern_tech_medium",
                "score_range": "70-84",
                "common_factors": "Good technical foundation, some missing keywords, limited quantification, basic project descriptions",
                "industry": "Technology", 
                "improvement_suggestions": "Add cloud certifications, quantify impact metrics, include modern frameworks, highlight problem-solving",
                "sample_size": "200+ resumes",
                "success_rate": "76%"
            },
            {
                "id": "pattern_finance_high",
                "score_range": "80-90",
                "common_factors": "Financial modeling expertise, relevant certifications, quantitative background, regulatory knowledge, risk management experience",
                "industry": "Finance",
                "improvement_suggestions": "Add advanced Excel skills, include P&L impact, highlight compliance experience",
                "sample_size": "100+ resumes",
                "success_rate": "89%"
            },
            {
                "id": "pattern_general_low",
                "score_range": "40-60",
                "common_factors": "Generic descriptions, missing keywords, poor formatting, no quantification, outdated skills",
                "industry": "General",
                "improvement_suggestions": "Complete skills overhaul needed, add industry keywords, quantify all achievements, modernize format",
                "sample_size": "300+ resumes",
                "success_rate": "34%"
            }
        ]
        
        # Populate collections
        try:
            # Add industry requirements
            if self.industry_collection.count() == 0:
                for item in industry_data:
                    metadata = {k: v for k, v in item.items() if k != "requirements"}
                    processed_metadata = self._process_metadata(metadata)
                    
                    self.industry_collection.add(
                        documents=[item["requirements"]],
                        metadatas=[processed_metadata],
                        ids=[item["id"]]
                    )
            
            # Add best practices
            if self.best_practices_collection.count() == 0:
                for item in best_practices_data:
                    metadata = {k: v for k, v in item.items() if k != "practice"}
                    processed_metadata = self._process_metadata(metadata)
                    
                    self.best_practices_collection.add(
                        documents=[item["practice"]],
                        metadatas=[processed_metadata],
                        ids=[item["id"]]
                    )
            
            # Add skills taxonomy
            if self.skills_collection.count() == 0:
                for item in skills_data:
                    metadata = {k: v for k, v in item.items()}
                    processed_metadata = self._process_metadata(metadata)
                    
                    self.skills_collection.add(
                        documents=[f"{item['skill']}: {item['category']} - {', '.join(item['related_skills'])}"],
                        metadatas=[processed_metadata],
                        ids=[item["id"]]
                    )
            
            # Add historical patterns
            if self.patterns_collection.count() == 0:
                for item in patterns_data:
                    metadata = {k: v for k, v in item.items() if k != "common_factors"}
                    processed_metadata = self._process_metadata(metadata)
                    
                    self.patterns_collection.add(
                        documents=[f"Score {item['score_range']}: {item['common_factors']}"],
                        metadatas=[processed_metadata],
                        ids=[item["id"]]
                    )
                        
        except Exception as e:
            st.warning(f"Knowledge base already populated or error occurred: {e}")

    # =============================================================================
    # RAG KNOWLEDGE BASE INTEGRATION METHODS
    # =============================================================================
    
    def get_intelligent_industry_insights(self, job_description: str, resume_text: str = None) -> str:
        """RAG: Industry-specific requirements analysis"""
        
        # 1. RETRIEVE
        industry_results = self.industry_collection.query(
            query_texts=[job_description],
            n_results=3
        )
        
        # 2. AUGMENT
        context = ""
        for i, doc in enumerate(industry_results['documents'][0]):
            metadata = industry_results['metadatas'][0][i]
            context += f"Industry: {metadata.get('industry', 'N/A')}\n"
            context += f"Requirements: {doc}\n"
            context += f"Key Skills: {metadata.get('key_skills', 'N/A')}\n"
            context += f"Experience Level: {metadata.get('experience_level', 'N/A')}\n"
            context += f"Salary Range: ${metadata.get('salary_range', 'N/A')}\n"
            context += f"Growth Trend: {metadata.get('growth_trend', 'N/A')}\n\n"
        
        prompt = f"""
        Based on industry-specific requirements data, provide insights for this job:

        INDUSTRY REQUIREMENTS:
        {context}

        JOB DESCRIPTION:
        {job_description}

        {"CANDIDATE RESUME: " + resume_text if resume_text else ""}

        Provide analysis on:
        1. Industry alignment and fit
        2. Required vs. preferred skills breakdown
        3. Experience level expectations
        4. Salary expectations and market trends
        5. Career growth opportunities
        {"6. Candidate's fit assessment" if resume_text else ""}

        Be specific and data-driven in your insights.
        """
        
        # 3. GENERATE
        return self._generate_llm_response(prompt, max_tokens=1200)

    def get_resume_optimization_recommendations(self, resume_text: str, job_description: str = None) -> str:
        """RAG: Best practices for resume optimization"""
        
        # 1. RETRIEVE
        practices_results = self.best_practices_collection.query(
            query_texts=["resume formatting keywords achievements ATS optimization"],
            n_results=4
        )
        
        # 2. AUGMENT
        practices_context = ""
        for i, doc in enumerate(practices_results['documents'][0]):
            metadata = practices_results['metadatas'][0][i]
            practices_context += f"Category: {metadata.get('category', 'N/A')}\n"
            practices_context += f"Best Practice: {doc}\n"
            practices_context += f"Importance: {metadata.get('importance', 'N/A')}\n"
            practices_context += f"ATS Impact: {metadata.get('ats_impact', 'N/A')}\n"
            practices_context += f"Success Rate: {metadata.get('success_rate', 'N/A')}\n\n"
        
        prompt = f"""
        Based on proven resume optimization best practices, analyze and improve this resume:

        BEST PRACTICES DATA:
        {practices_context}

        RESUME TO OPTIMIZE:
        {resume_text}

        {"TARGET JOB: " + job_description if job_description else ""}

        Provide specific optimization recommendations for:
        1. Formatting and structure improvements
        2. Keyword optimization strategies
        3. Achievement quantification opportunities  
        4. ATS compatibility enhancements
        5. Section-by-section improvements

        Include specific examples and before/after suggestions where possible.
        """
        
        # 3. GENERATE
        return self._generate_llm_response(prompt, max_tokens=1500)

    def get_intelligent_skill_matching(self, resume_skills: List[str], job_description: str) -> str:
        """RAG: Advanced skill taxonomy and keyword matching"""
        
        # 1. RETRIEVE
        skills_query = " ".join(list(resume_skills)[:10])  # Limit to avoid token limits
        skills_results = self.skills_collection.query(
            query_texts=[skills_query],
            n_results=5
        )
        
        industry_results = self.industry_collection.query(
            query_texts=[job_description],
            n_results=2
        )
        
        # 2. AUGMENT
        skills_context = ""
        for i, doc in enumerate(skills_results['documents'][0]):
            metadata = skills_results['metadatas'][0][i]
            skills_context += f"Skill: {metadata.get('skill', 'N/A')}\n"
            skills_context += f"Category: {metadata.get('category', 'N/A')}\n"
            skills_context += f"Related Skills: {metadata.get('related_skills', 'N/A')}\n"
            skills_context += f"Industry Relevance: {metadata.get('industry_relevance', 'N/A')}\n"
            skills_context += f"Demand Level: {metadata.get('demand_level', 'N/A')}\n"
            skills_context += f"Salary Impact: {metadata.get('salary_impact', 'N/A')}\n\n"
        
        industry_context = ""
        for i, doc in enumerate(industry_results['documents'][0]):
            metadata = industry_results['metadatas'][0][i]
            industry_context += f"Industry: {metadata.get('industry', 'N/A')}\n"
            industry_context += f"Required Skills: {metadata.get('key_skills', 'N/A')}\n\n"
        
        prompt = f"""
        Based on comprehensive skill taxonomy and industry requirements, analyze skill alignment:

        SKILL TAXONOMY DATA:
        {skills_context}

        INDUSTRY REQUIREMENTS:
        {industry_context}

        CANDIDATE SKILLS: {', '.join(resume_skills)}
        JOB DESCRIPTION: {job_description}

        Provide detailed analysis on:
        1. Direct skill matches and strength assessment
        2. Adjacent/transferable skills identification  
        3. Critical missing skills with priority ranking
        4. Skill development pathway recommendations
        5. Market demand and salary impact analysis
        6. Alternative skill expressions and synonyms to include

        Focus on actionable insights for both immediate application and long-term career growth.
        """
        
        # 3. GENERATE
        return self._generate_llm_response(prompt, max_tokens=1500)

    def get_historical_scoring_insights(self, current_score: int, resume_text: str, job_description: str) -> str:
        """RAG: Historical scoring patterns analysis"""
        
        # 1. RETRIEVE
        patterns_results = self.patterns_collection.query(
            query_texts=[f"score {current_score} resume patterns"],
            n_results=3
        )
        
        # 2. AUGMENT
        patterns_context = ""
        for i, doc in enumerate(patterns_results['documents'][0]):
            metadata = patterns_results['metadatas'][0][i]
            patterns_context += f"Score Range: {metadata.get('score_range', 'N/A')}\n"
            patterns_context += f"Pattern: {doc}\n"
            patterns_context += f"Industry: {metadata.get('industry', 'N/A')}\n"
            patterns_context += f"Improvements: {metadata.get('improvement_suggestions', 'N/A')}\n"
            patterns_context += f"Sample Size: {metadata.get('sample_size', 'N/A')}\n"
            patterns_context += f"Success Rate: {metadata.get('success_rate', 'N/A')}\n\n"
        
        prompt = f"""
        Based on historical scoring patterns from similar resumes, provide predictive insights:

        HISTORICAL PATTERNS DATA:
        {patterns_context}

        CURRENT RESUME SCORE: {current_score}/100
        RESUME: {resume_text[:1000]}...
        JOB TARGET: {job_description[:500]}...

        Analyze and predict:
        1. Score interpretation based on historical data
        2. Common factors that led to this score range
        3. Probability of interview callbacks at this score
        4. Specific improvement strategies proven effective for similar scores
        5. Expected score improvement timeline with recommended changes
        6. Industry-specific benchmarking

        Provide data-driven, actionable insights with realistic timelines and expectations.
        """
        
        # 3. GENERATE
        return self._generate_llm_response(prompt, max_tokens=1500)

    def store_analysis_in_database(self, user_id: int, resume_id: int, job_id: int, 
                                 ats_score: int, rag_insights: Dict[str, str]) -> int:
        """Store RAG-enhanced analysis results in database"""
        
        session = SessionLocal()
        try:
            # Combine all RAG insights into comprehensive feedback and recommendations
            combined_feedback = f"""
            INDUSTRY INSIGHTS:
            {rag_insights.get('industry_insights', 'N/A')}

            OPTIMIZATION RECOMMENDATIONS:
            {rag_insights.get('optimization_recommendations', 'N/A')}

            SKILL ANALYSIS:
            {rag_insights.get('skill_matching', 'N/A')}
            """
            
            combined_recommendations = f"""
            HISTORICAL SCORING INSIGHTS:
            {rag_insights.get('scoring_insights', 'N/A')}

            PRIORITIZED ACTION ITEMS:
            Based on the analysis above, focus on these key areas for maximum impact.
            """
            
            # Create new score record with RAG-enhanced data
            score_record = Score(
                resume_id=resume_id,
                job_id=job_id,
                score=ats_score,
                feedback=combined_feedback,
                recommendations=combined_recommendations
            )
            
            session.add(score_record)
            session.commit()
            
            return score_record.id
        
        except Exception as e:
            session.rollback()
            st.error(f"Error storing RAG analysis: {e}")
            return None
        finally:
            session.close()

    # =============================================================================
    # INTEGRATED RAG ANALYSIS METHOD (Main Entry Point)
    # =============================================================================
    
    def run_complete_rag_analysis(self, resume_text: str, job_description: str, 
                                current_score: int, resume_skills: List[str]) -> Dict[str, str]:
        """
        Run complete RAG analysis integrating all knowledge base components
        This is the main method to call from your existing app
        """
        
        st.info("Running intelligent knowledge base analysis...")
        
        rag_results = {}
        
        with st.spinner("Analyzing industry requirements..."):
            rag_results['industry_insights'] = self.get_intelligent_industry_insights(
                job_description, resume_text
            )
        
        with st.spinner("Generating optimization recommendations..."):
            rag_results['optimization_recommendations'] = self.get_resume_optimization_recommendations(
                resume_text, job_description
            )
        
        with st.spinner("Performing advanced skill matching..."):
            rag_results['skill_matching'] = self.get_intelligent_skill_matching(
                resume_skills, job_description
            )
        
        with st.spinner("Analyzing historical scoring patterns..."):
            rag_results['scoring_insights'] = self.get_historical_scoring_insights(
                current_score, resume_text, job_description
            )
        
        return rag_results