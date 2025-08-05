# Invoice Analyzer

Invoice Analyzer is a Streamlit web application that uses Google's Gemini AI model to analyze invoice images and answer user queries about them. 

Simply upload an invoice image and ask any question related to the invoice and the AI agent will extract and provide the relevant information.

## Features

- Upload invoice images in JPG, JPEG, or PNG format
- Ask natural language questions about the invoice
- AI-powered extraction and analysis using Gemini Pro Vision model
- Simple and interactive Streamlit interface

## Setup

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone the repository:**

   ```sh
   git clone <your-repo-url>
   cd invoice-extractor
   ```

2. **Create and activate a virtual environment:**

   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up your Google API key:**

   - Create a `.env` file in the project root (already present in this repo).
   - Add your Google API key:
     ```
     GOOGLE_API_KEY="your-google-api-key"
     ```

## Usage

1. **Run the Streamlit app:**

   ```sh
   streamlit run app.py
   ```

2. **Open your browser to the provided local URL.**

3. **Upload an invoice image and enter your query.**

4. **Click "Tell more about this invoice" to get the AI's response.**

## File Structure

- `app.py` — Main Streamlit application
- `requirements.txt` — Python dependencies
- `.env` — Environment variables (API keys)
- `.gitignore` — Files and folders to ignore in git

## Example

1. Upload an invoice image.
2. Enter a query like:  
   *"What is the total amount on this invoice?"*
3. The AI will analyze the image and provide an answer.

## License

This project is for educational purposes.
