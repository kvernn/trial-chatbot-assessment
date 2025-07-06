# Mindhive AI Chatbot Engineer Assessment

This repository contains the full implementation for the Mindhive AI Chatbot Engineer technical assessment. The project is a multi-tool chatbot assistant for "ZUS Coffee," capable of performing calculations, answering questions about products using a Retrieval-Augmented Generation (RAG) pipeline, and querying for outlet information using a Text-to-SQL pipeline.


## Architecture Overview

The project is designed with a decoupled, service-oriented architecture to promote scalability and separation of concerns. It consists of two main components:

- **Chatbot Agent Application (`app/`):** A Python application that runs the main conversational agent. This agent is the "brain" of the operation, responsible for understanding user intent, managing conversation history, and deciding which tool to use.
- **FastAPI Data Services (`api/`):** A backend API server that exposes specialized data endpoints. The agent consumes these services as tools. This separation allows the data retrieval logic (RAG, Text2SQL) to be developed, scaled, and maintained independently of the agent's core logic.


### Key Design Trade-offs

*   **Decoupled Architecture (Agent + API):** Chosen over a monolithic structure for better scalability and maintainability. It mirrors a real-world scenario where a chatbot consumes external or microservice-based APIs.
*   **FAISS for Vector Store:** Selected for its simplicity and efficiency as a local, file-based vector store. This avoids the complexity and cost of setting up a cloud-based service like Pinecone, making the project easy for anyone to clone and run.
*   **SQLite for Structured Data:** Used for the outlet database because it is serverless, file-based, and integrates seamlessly with Python and LangChain. It's a lightweight and portable solution perfect for this assessment's scope.
*   **Tool Error Handling:** Tool functions (like the calculator and API callers) include `try-except` blocks. Instead of letting the agent crash, errors are caught and returned as a textual "Observation." This allows the LLM to formulate a graceful, user-friendly response about the failure, which is a more robust approach than simply terminating.

---

## Features & Implemented Assessment Parts

*   **Part 1: Sequential Conversation:** The agent maintains conversation history using `ConversationBufferMemory`, allowing it to understand context in follow-up questions.
*   **Part 2: Agentic Planning:** The agent uses a sophisticated planner/controller loop (`AgentExecutor`) to parse user intent, select the appropriate tool, or respond directly. A detailed write-up can be found in [`PART2_AGENT_PLANNING.md`](./PART2_AGENT_PLANNING.md).
*   **Part 3: Tool Calling:** A `Calculator` tool is integrated with robust error handling for invalid expressions.
*   **Part 4: Custom API & RAG Integration:**
    *   A **RAG pipeline** for ZUS drinkware products is exposed via the `/products` FastAPI endpoint.
    *   A **Text-to-SQL pipeline** for ZUS outlet information is exposed via the `/outlets` FastAPI endpoint.
    *   The chatbot agent is equipped with tools to consume both of these custom API endpoints.
*   **Part 5: Unhappy Flows:** The system is tested for robustness against missing parameters, API downtime (simulated with `pytest-mock`), and malicious payloads (SQL injection). See `tests/test_part5_unhappy_flows.py`.

---

## Setup & Run Instructions

### Prerequisites

*   Python 3.9+
*   Git

### 1. Clone the Repository

```
git clone https://github.com/kvernn/trial-chatbot-assessment.git
cd trial-chatbot-assessment
```

### 2. Setup Virtual Environment
```
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Install Dependencies
Create a ```.env``` file in the root directory of the project. This file will store your OpenAI API key:
```
OPENAI_API_KEY="your_openai_api_key_here"
```

### 5. Ingest Data
Run the data ingestion scripts to create the local FAISS vector store for products and the SQLite database for outlets.
```
python scripts/ingest_products.py
python scripts/ingest_outlets.py
```

### 6. Ingest Data
In one terminal, start the FastAPI server:
```
uvicorn api.main:app --reload
```

### 7. Run the Chatbot
In a second terminal, start the interactive chatbot agent:
```
python app/chatbot.py
```


### You can now start asking the chatbot questions!
