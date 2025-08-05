from dotenv import load_dotenv
import os
load_dotenv()
import streamlit as st
import sqlite3

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load google gemini model and provide sql query as response
def get_gemini_response(question,prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([prompt[0], question])
    return response.text

# Functin to retrieve query results from the database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    current = conn.cursor()
    current.execute(sql)
    rows = current.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        print(row)
    return rows

# Define the prompt
prompt = ["""
You are a SQL expert. You will be given a question and you need to provide the SQL query to answer that question.
The question will be related to a student database with the following schema: Name, Class, Section, Marks.
You will also be given the database name as 'student.db'.
E.g. How many students are there in the class Data Science?
The SQL query to answer this question is: select count(*) from student where class = 'Data Science';
E.g. What is the average marks of students in section B?
The SQL query to answer this question is: select avg(marks) from student where section = 'B';
the sql code should not have ``` at the start and end of the code.
"""
]

# Streamlit app
st.title("Text to SQL with Google Gemini")
question = st.text_input("Enter your question about the student database:")
submit = st.button("Submit")

if submit:
    response = get_gemini_response(question, prompt)
    print(response)
    data = read_sql_query(response, 'student.db')
    st.subheader("Query Results:")
    for row in data:
        print(row)
        st.header(row)