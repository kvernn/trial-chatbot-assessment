# --- app/chatbot.py ---
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os

load_dotenv()

# --- Configuration ---
# Using OpenAI's Model/Key with a temperature of 0.7
try:
    llm = ChatOpenAI(temperature=0.7)
except Exception as e:
    print(f"Error initializing LLM. Do you have OPENAI_API_KEY set in your .env file? Error: {e}")
    print("Exiting. Please set up your LLM configuration.")
    exit()


# --- Memory ---
memory = ConversationBufferMemory()

# --- Conversation Chain ---
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# --- Interaction Loop ---
def run_chat():
    print("Chatbot activated! Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break

        response = conversation.predict(input=user_input)
        print(f"Bot: {response}")

if __name__ == "__main__":
    run_chat()