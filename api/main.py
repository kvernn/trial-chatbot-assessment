# api/main.py

from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel # Not needed if we remove the model
from dotenv import load_dotenv
import os
from pathlib import Path

# --- COMMENT OUT HEAVY RAG IMPORTS ---
# from langchain_community.vectorstores import FAISS
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain.chains import create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain_core.prompts import ChatPromptTemplate

# Imports for Text2SQL Logic (KEEP THESE)
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI # Still need this for Text2SQL

load_dotenv()

app = FastAPI(
    title="Mindhive Assessment Chatbot API",
    description="Provides endpoints for ZUS Coffee product knowledge (RAG) and outlet information (Text2SQL).",
    version="1.0.0"
)

# Re-use the llm instance for the SQL chain
llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo")


# --- FAKE RAG ENDPOINT (REPLACES REAL ONE) ---
# This section is a placeholder for the demo to avoid large dependencies.
# The full RAG logic is available in the 'main' branch of the repository.
print("RAG components are MOCKED for this deployment.")
rag_chain = True # Set to a non-None value to pass the check in the endpoint


# --- Initialize Text2SQL components (on startup) ---
PROJECT_ROOT = Path(os.environ.get('LAMBDA_TASK_ROOT', '.'))
SQLITE_DB_PATH = PROJECT_ROOT / "db" / "outlets.db"
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
async def get_product_info_mock(query: str):
    """
    MOCKED ENDPOINT for demo purposes. Returns a canned response.
    The full RAG implementation is in the main branch.
    """
    print(f"Received query for MOCKED /products endpoint: {query}")
    if "tumbler" in query.lower():
        return {"summary": "This is a mocked response for a ZUS Tumbler. It has great insulation and comes in many colors. The full RAG implementation can be run locally.", "query": query}
    else:
        return {"summary": "This is a mocked response. My knowledge base for this demo is limited. The full RAG implementation can be run locally.", "query": query}


# --- KEEP THE REAL OUTLETS ENDPOINT ---
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