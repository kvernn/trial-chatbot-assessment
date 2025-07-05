# scripts/ingest_products.py
import json
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

print("Starting ingestion process...")

# Load environment variables from .env file (for OPENAI_API_KEY)
load_dotenv()

# --- 1. Load the Data ---
# Define the path to the JSON file
json_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'zus_drinkware_products.json')

print(f"Loading data from: {json_file_path}")
with open(json_file_path, 'r', encoding='utf-8') as f:
    products_data = json.load(f)

# --- 2. Prepare Documents for LangChain ---
# We need to convert our JSON objects into a format LangChain can use (Document objects).
# We'll combine the relevant fields into a single text block for each product.
documents = []
for product in products_data:
    # Combine name, description, and features into a single content string
    content = f"Product Name: {product['name']}\n"
    content += f"Price: {product['price']}\n"
    content += f"Description: {product['description']}\n"
    content += "Features:\n" + "\n".join([f"- {feat}" for feat in product['features']])

    # Create a LangChain Document object
    # We can also store metadata, which can be useful for filtering later if needed.
    doc = Document(
        page_content=content,
        metadata={
            "name": product['name'],
            "price": product['price'],
            "url": product['url']
        }
    )
    documents.append(doc)

print(f"Loaded and prepared {len(documents)} documents.")

# --- 3. Split Documents into Chunks ---
# This is important for RAG. Large documents are split into smaller chunks
# to ensure the most relevant parts are retrieved.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
split_documents = text_splitter.split_documents(documents)
print(f"Split documents into {len(split_documents)} chunks.")

# --- 4. Create Embeddings and Ingest into Vector Store (FAISS) ---
# Initialize the embeddings model (using OpenAI's model)
print("Initializing embeddings model...")
embeddings = OpenAIEmbeddings()

print("Creating FAISS vector store from documents...")
# FAISS.from_documents will create embeddings for each chunk and build the index.
vector_store = FAISS.from_documents(split_documents, embeddings)

# --- 5. Save the Vector Store Locally ---
# Define the path to save the FAISS index
faiss_index_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'faiss_product_index')
print(f"Saving FAISS index to: {faiss_index_path}")
vector_store.save_local(faiss_index_path)

print("Ingestion complete! FAISS index saved successfully.")