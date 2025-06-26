import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Test for Part 1
import pytest
from app.chatbot import llm
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

def test_happy_path_three_turns():
    """Test a simple three-turn conversation where context should be maintained."""
    memory = ConversationBufferMemory()
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )

    # Turn 1
    response1_text = conversation.predict(input="Are there any good cafes in Bangsar?")
    assert response1_text is not None
    print(f"\nHappy Path - Turn 1 Human: Are there any good cafes in Bangsar?")
    print(f"Happy Path - Turn 1 AI: {response1_text}")

    # Turn 2
    response2_text = conversation.predict(input="What about VCR?")
    assert response2_text is not None
    print(f"Happy Path - Turn 2 Human: What about VCR?")
    print(f"Happy Path - Turn 2 AI: {response2_text}")

    # Turn 3
    response3_text = conversation.predict(input="What are their opening hours?")
    assert response3_text is not None
    print(f"Happy Path - Turn 3 Human: What are their opening hours?")
    print(f"Happy Path - Turn 3 AI: {response3_text}")

    assert "Bangsar" in memory.chat_memory.messages[0].content # First msg
    assert "VCR" in memory.chat_memory.messages[2].content     # Second msg
    assert len(memory.chat_memory.messages) == 6 # 3 human, 3 AI msg


def test_interrupted_path():
    """Test a conversation where the user changes topic or provides irrelevant info."""
    memory = ConversationBufferMemory()
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )

    # Turn 1
    response1_text = conversation.predict(input="Tell me about the weather in Kuala Lumpur.")
    assert response1_text is not None
    print(f"\nInterrupted Path - Turn 1 Human: Tell me about the weather in Kuala Lumpur.")
    print(f"Interrupted Path - Turn 1 AI: {response1_text}")


    # Turn 2 - Interruption / Irrelevant
    response2_text = conversation.predict(input="My favorite color is blue.")
    assert response2_text is not None
    print(f"Interrupted Path - Turn 2 Human: My favorite color is blue.")
    print(f"Interrupted Path - Turn 2 AI: {response2_text}")

    # Turn 3 - Attempt to return to original topic
    response3_text = conversation.predict(input="So, is it going to rain there today?")
    assert response3_text is not None
    print(f"Interrupted Path - Turn 3 Human: So, is it going to rain there today?")
    print(f"Interrupted Path - Turn 3 AI: {response3_text}")

    assert len(memory.chat_memory.messages) == 6