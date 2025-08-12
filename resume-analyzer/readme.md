# Resume Analyzer

This Streamlit app analyzes your resume against a job description. It extracts text from your PDF resume, sends it to Gemini model for evaluation, and displays a detailed match analysis, missing keywords, and feedback to help you improve your resume for tech roles.

## Features

- Upload your resume in PDF format
- Paste a job description for analysis
- JD-Resume matching percentage displayed
- List of missing keywords
- Actionable feedback summary

## How It Works

1. **Upload Resume:** Select your resume PDF file.
2. **Paste Job Description:** Enter the job description in the provided text area.
3. **Analyze:** Click "Analyze my Resume" to get instant feedback.

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd resume-analyzer
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up your Google Gemini API key:**
   - Create a `.env` file in the project root.
   - Add your API key:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

4. **Run the app:**
   ```sh
   streamlit run app.py
   ```
