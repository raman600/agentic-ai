from dotenv import load_dotenv
from PIL import Image

import streamlit as st
import google.generativeai as genai

import os

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Load Gemini Provision Model
model = genai.GenerativeModel('gemini-2.5-pro')

def get_gemini_response(input, image, prompt):
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to convert image file to the bytes format
def input_image_details(uploaded_file):
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No image file uploaded.")


## initialize Streamlit app

st.set_page_config(page_title="Invoice Extractor")
st.header("Invoice Extractor")
input = st.text_input("Enter your query", key="input")
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="image")

image=""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

submit = st.button("Tell more about this invoice")


input_prompt = """
you are an AI assistant that extracts information from invoices. i will upload an image of an invoice and ask you a question about it.
you will answer my question based on the information in the invoice image.
"""

if submit:
    image_data = input_image_details(uploaded_file)
    response = get_gemini_response(input_prompt, image_data, input)
    st.subheader("Response -- ")
    st.write(response)