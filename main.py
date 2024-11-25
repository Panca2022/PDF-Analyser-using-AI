import os
import fitz  # PyMuPDF
import faiss
import numpy as np
import openai
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI
app = FastAPI()

# Directory to store uploaded PDFs
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

# Initialize OpenAI API key
openai.api_key = OPENAI_API_KEY

# Data model for questions
class QuestionRequest(BaseModel):
    file_name: str
    question: str

# Function to extract text from a PDF using PyMuPDF
def extract_pdf_text(file_path: str) -> str:
    """Extracts text from a PDF file."""
    try:
        doc = fitz.open(file_path)
        text_content = ""
        for page in doc:
            text_content += page.get_text("text")
        return text_content.strip()
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")

# Function to get text embeddings using OpenAI API
def get_text_embeddings(text: str) -> np.ndarray:
    """Converts text into embeddings using OpenAI's new Embedding API."""
    try:
        response = openai.embeddings.create(
            model="text-embedding-ada-002",  # You can change the model if necessary
            input=[text]  # The text that needs to be converted into an embedding
        )
        # Returning the embedding from the response
        return np.array(response['data'][0]['embedding'])
    except openai.error.AuthenticationError as e:
        logging.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
    except openai.error.RateLimitError as e:
        logging.error(f"Rate limit exceeded: {str(e)}")
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded: {str(e)}")
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def process_question_with_faiss(pdf_text: str, question: str) -> str:
    """Use FAISS to index document text and find an answer to the question."""
    try:
        # Split the document text into chunks (e.g., sentences or paragraphs)
        text_chunks = pdf_text.split("\n")  # Split by newline as a simple example

        # Generate embeddings for each text chunk
        text_embeddings = np.array([get_text_embeddings(chunk) for chunk in text_chunks])

        # Generate the question embedding
        question_embedding = get_text_embeddings(question)

        # Create a FAISS index and add the text chunk embeddings
        index = faiss.IndexFlatL2(text_embeddings.shape[1])  # L2 distance for cosine similarity
        index.add(text_embeddings)

        # Perform a similarity search with the question embedding
        _, I = index.search(np.array([question_embedding]), k=1)

        # Retrieve and return the most similar text chunk as the answer
        return f"Answer: {text_chunks[I[0][0]]}"

    except Exception as e:
        logging.error(f"Error processing question with FAISS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF, extract its text, and store it for further use.
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Save the uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logging.info(f"File '{file.filename}' uploaded successfully.")
    except Exception as e:
        logging.error(f"Failed to save uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    # Extract text from the uploaded PDF
    try:
        text_content = extract_pdf_text(file_path)
        logging.info(f"Extracted text from file '{file.filename}' preview: {text_content[:500]}")
        return JSONResponse(content={
            "message": f"File '{file.filename}' uploaded and processed successfully.",
            "text_preview": text_content[:500]  # Preview the first 500 characters
        })
    except Exception as e:
        logging.error(f"Failed to process PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

import traceback

@app.post("/ask/")
async def ask_question(question_request: QuestionRequest):
    try:
        file_name = question_request.file_name
        question_text = question_request.question

        # Validate input
        if not file_name or not question_text:
            raise HTTPException(status_code=400, detail="File name and question must be provided.")

        # Check if the file exists
        file_path = os.path.join(UPLOAD_DIR, file_name)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF file not found. Please upload the PDF first.")

        # Extract text from the PDF
        pdf_text = extract_pdf_text(file_path)
        print(f"Extracted PDF text: {pdf_text[:500]}...")  # Log a preview of the text

        # Get the answer using FAISS for similarity search
        answer = process_question_with_faiss(pdf_text, question_text)

        # Return the answer
        return {"answer": answer}

    except Exception as e:
        # Log the detailed exception
        error_details = traceback.format_exc()
        print(f"Error occurred: {error_details}")  # Print the detailed error trace for debugging
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")
