Resume RAG Agent

## Overview

**Resume RAG Agent** is an intelligent resume analysis tool powered by Retrieval-Augmented Generation (RAG) and LLM agents. It extracts, scores, and improves resumes against job descriptions, providing actionable feedback and industry insights. The app uses Streamlit for its UI and integrates with a knowledge base and database for historical tracking and advanced recommendations.

---

## Features

- **Resume Extraction:** Upload PDF, DOCX, or TXT resumes for automated parsing.
- **Job Description Analysis:** Paste or upload job descriptions for skill and requirement extraction.
- **ATS Scoring:** Scores resumes using LLM agents and RAG context for consistent, objective results.
- **Improvement Suggestions:** Provides targeted recommendations to optimize resumes for ATS and recruiters.
- **Industry & Skill Insights:** Leverages a knowledge base for industry trends, skill matching, and best practices.
- **Job Search:** Integrated job search using DuckDuckGo or Serper API.

---

## Workflow

1. **User uploads a resume and provides a job description.**
2. **Resume and job description are extracted and processed using Autogen agents.**
3. **Resume is scored against the job description using RAG context and LLM agents.**
4. **Improvement suggestions are generated and displayed.**
5. **RAG Knowledge Base provides industry, skill, and historical performance insights.**
6. **Results, feedback, and scores are cached and stored in the database for future reference.**
7. **User can search for jobs and view resume history.**

---

## Quick Start

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Add your OpenAI API key and Serper API key to a `.env` file:
     ```
     OPENAI_API_KEY=your_openai_key
     SERPER_API_KEY=your_serper_key
     ```

3. **Run the app:**
   ```
   streamlit run app_rag_final.py
   ```

---

## Project Structure

- `app_rag_final.py` — Main Streamlit UI and workflow.
- `process.py` — Resume/job extraction, normalization, and caching.
- `score.py` — Resume scoring logic and agent configuration.
- `setup.py` — Agent setup and configuration.
- `rag.py` — RAG knowledge base and insights.
- `feedback.py` — Improvement suggestions, feedback, and job search.
- `db.py` — Database models and history tracking.

---
