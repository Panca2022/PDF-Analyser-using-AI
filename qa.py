from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import VectorDBQA

# Function to process the extracted PDF text and answer a question
def get_answer_from_pdf(extracted_text: str, question: str) -> str:
    """
    Process the extracted PDF text and find an answer to the given question.
    """
    try:
        # Split the text into manageable chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_text(extracted_text)

        # Generate embeddings for text chunks
        embeddings = OpenAIEmbeddings()

        # Create a vector store for document search
        docsearch = FAISS.from_texts(texts, embeddings)

        # Define the LLM model for question-answering
        llm = OpenAI()

        # Create the QA chain using the vector store
        qa_chain = VectorDBQA(combine_docs_chain=load_qa_chain(llm), vectorstore=docsearch)

        # Run the QA chain to get the answer
        result = qa_chain.run(question)
        return result

    except Exception as e:
        raise Exception(f"Error in processing QA: {str(e)}")
