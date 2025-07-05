# app/chatbot.py

# --- Core LangChain and OpenAI imports ---
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os

# --- Imports for Agent and Tools (NEW for Part 3) ---
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain.chains import LLMMathChain

# Load environment variables
load_dotenv()

# --- Configuration ---
try:
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
except Exception as e:
    print(f"Error initializing LLM. Do you have OPENAI_API_KEY set and funded? Error: {e}")
    print("Exiting. Please set up your LLM configuration.")
    exit()


# --- Memory (Slight modification for agent) ---
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


# --- Tools ---
# Calculator Tool
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)

def safe_calculator_run(query: str) -> str:
    """
    Wraps llm_math_chain.run to catch exceptions and return a user-friendly error string.
    This string will become the 'observation' for the agent.
    """
    try:
        return llm_math_chain.run(query)
    except Exception as e:
        error_message = f"Error performing calculation: {str(e)}. Please ensure your input is a valid mathematical expression with numbers."
        print(f"[safe_calculator_run] Caught error: {error_message}")
        return f"The calculator tool reported an error: {str(e)}. It can only handle valid mathematical expressions."


calculator_tool = Tool(
    name="Calculator",
    func=safe_calculator_run,
    description="Useful for when you need to answer questions about math. Input should be a fully formed mathematical question or expression.",
)

tools = [calculator_tool]


# --- Agent Prompt ---
AGENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. You have access to a calculator tool to help with math questions. For other questions, answer them directly based on your knowledge. If you use the calculator, tell the user the result of the calculation."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


# --- Agent Setup ---
agent = create_openai_tools_agent(llm, tools, AGENT_PROMPT)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors="I'm having a bit of trouble with that request. Could you please rephrase or try something else?"
)

# --- Interaction Loop (Modified to use AgentExecutor) ---
def run_chat():
    print("Chatbot Agent (with Calculator) activated! Type 'exit' to end the conversation.")
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