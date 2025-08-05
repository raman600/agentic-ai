# Text-to-SQL 
This project enables the conversion of natural language queries into SQL statements using Google Gemini. It enables users to interact with a student database without requiring SQL expertise.

## Features

- **Natural Language to SQL**: Automatically translates user questions into SQL queries.
- **Streamlit Web Application**: Simple and interactive web interface.
- **SQLite Database**: Stores and manages student data.
- **Secure API Integration**: Utilizes environment variables for API key management.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Installation

1. **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd text-to-sql
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Configure environment variables:**
    - Create a `.env` file in the project root:
      ```
      GOOGLE_API_KEY="your-google-api-key"
      ```

4. **Initialize the database:**
    ```sh
    python sql.py
    ```

5. **Launch the application:**
    ```sh
    streamlit run app.py
    ```

## Usage

- Enter your question about the student database in plain English.
- The application will generate and execute the corresponding SQL query.
- Results will be displayed in the web interface.

### Example Queries

- "List all students in section A."
- "What is the average marks in the Data Science class?"

## Project Structure

```
.
├── app.py           # Streamlit application
├── sql.py           # Database setup script
├── student.db       # SQLite database file
├── requirements.txt # Python dependencies
├── .env             # Environment variables (not included here)
└── .gitignore       # Git ignore file
```

## License

This project is for educational purposes.
