# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import os

# Imports for RAG Logic
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Imports for Text2SQL Logic
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain

load_dotenv()

app = FastAPI(
    title="Mindhive Assessment Chatbot API",
    description="Provides endpoints for ZUS Coffee product knowledge (RAG) and outlet information (Text2SQL).",
    version="1.0.0"
)

# --- Define Project Root and Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FAISS_INDEX_PATH = PROJECT_ROOT / "db" / "faiss_product_index"
SQLITE_DB_PATH = PROJECT_ROOT / "db" / "outlets.db"


# --- Initialize RAG components (on startup) ---
try:
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.load_local(str(FAISS_INDEX_PATH), embeddings, allow_dangerous_deserialization=True)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo")
    rag_prompt = ChatPromptTemplate.from_template("""You are an assistant for question-answering tasks for ZUS Coffee products. Use the following pieces of retrieved context to answer the question. If you don't know the answer from the context, just say that you don't have information on that. Be concise and helpful.
    Question: {input}
    Context: {context}
    Answer:""")
    document_chain = create_stuff_documents_chain(llm, rag_prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain)
    print("RAG components loaded successfully.")
except Exception as e:
    print(f"Error loading RAG components: {e}")
    rag_chain = None

# --- Initialize Text2SQL components (on startup) ---
try:
    db = SQLDatabase.from_uri(f"sqlite:///{str(SQLITE_DB_PATH)}")
    sql_query_chain = create_sql_query_chain(llm, db)
    print("Text2SQL components loaded successfully.")
except Exception as e:
    print(f"Error loading Text2SQL components: {e}")
    sql_query_chain = None
    db = None

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "API is running", "message": "Welcome!"}

@app.get("/products", response_model=dict)
async def get_product_info(query: str):
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG system is not available.")
    try:
        response = await rag_chain.ainvoke({"input": query})
        return {"summary": response.get("answer", "No answer could be generated."), "query": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during RAG chain invocation: {e}")

@app.get("/outlets", response_model=dict)
async def get_outlet_info(query: str):
    if not sql_query_chain or not db:
        raise HTTPException(status_code=500, detail="Text2SQL system is not available.")
    try:
        sql_query = await sql_query_chain.ainvoke({"question": query})
        print(f"Generated SQL Query: {sql_query}")

        query_result = db.run(sql_query)
        print(f"SQL Query Result: {query_result}")

        return {
            "results": str(query_result),
            "query": query,
            "sql_query": sql_query
        }
    except Exception as e:
        print(f"Error during Text2SQL processing: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing your request: {e}")