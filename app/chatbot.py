# app/chatbot.py

import os
import requests
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain.chains import LLMMathChain

# Load environment variables from .env file
load_dotenv()

# --- 1. LLM Configuration ---
try:
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
except Exception as e:
    print(f"Error initializing LLM: {e}")
    exit()

# --- 2. Conversation Memory ---
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


# --- 3. Tool Definitions ---

# Tool 3a: Calculator
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=False)

def safe_calculator_run(query: str) -> str:
    """Wraps the math chain to handle execution errors."""
    try:
        return llm_math_chain.run(query)
    except Exception as e:
        return f"The calculator tool reported an error: {str(e)}."

# Tool 3b: ZUS Product Knowledge Base (RAG API)
def get_product_info(query: str) -> str:
    """Makes a request to the /products RAG API endpoint."""
    try:
        response = requests.get("http://127.0.0.1:8000/products", params={"query": query})
        response.raise_for_status()
        return response.json().get("summary", "No summary found.")
    except requests.exceptions.RequestException as e:
        return f"API Error: Could not connect to the product knowledge base. Details: {e}"

# Tool 3c: ZUS Outlet Information (Text2SQL API)
def get_outlet_info(query: str) -> str:
    """Makes a request to the /outlets Text2SQL API endpoint."""
    try:
        response = requests.get("http://127.0.0.1:8000/outlets", params={"query": query})
        response.raise_for_status()
        data = response.json()
        return f"Query Result: {data.get('results', 'No results found.')}"
    except requests.exceptions.RequestException as e:
        return f"API Error: Could not connect to the outlet information service. Details: {e}"

# --- 4. Tool Instantiation and List ---
calculator_tool = Tool(
    name="Calculator",
    func=safe_calculator_run,
    description="Useful for when you need to answer questions about math. Input should be a fully formed mathematical question or expression.",
)

product_knowledge_base_tool = Tool(
    name="ZUS_Product_Knowledge_Base",
    func=get_product_info,
    description="Use this tool to answer questions about ZUS Coffee drinkware products, such as tumblers, cups, and mugs. Ask about features, materials, prices, and descriptions.",
)

outlet_information_tool = Tool(
    name="ZUS_Outlet_Information",
    func=get_outlet_info,
    description="Use this tool to answer questions about ZUS Coffee outlet locations, addresses, operating hours, and available services like delivery or dine-in.",
)

tools = [calculator_tool, product_knowledge_base_tool, outlet_information_tool]


# --- 5. Agent Prompt ---
AGENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", """You are a helpful ZUS Coffee assistant. You have access to three tools:
        1. A Calculator for math questions.
        2. A ZUS_Product_Knowledge_Base for questions about ZUS drinkware products.
        3. A ZUS_Outlet_Information tool for questions about store locations, hours, and services.

        For any other questions, answer them directly based on your own knowledge.
        Provide clear and concise answers based on the tool's output."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


# --- 6. Agent and Executor Setup ---
agent = create_openai_tools_agent(llm, tools, AGENT_PROMPT)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors="I'm having a bit of trouble with that request. Could you please rephrase or try something else?"
)


# --- 7. Main Interaction Loop ---
def run_chat():
    print("ZUS Coffee Assistant activated! I can product info and outlet locations. Type 'exit' to end.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break

        try:
            response_dict = agent_executor.invoke({"input": user_input})
            print(f"Bot: {response_dict['output']}")
        except Exception as e:
            print(f"Bot System Error: An unexpected issue occurred in the agent: {e}")


if __name__ == "__main__":
    run_chat()