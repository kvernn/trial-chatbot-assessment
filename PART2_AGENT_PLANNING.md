# Part 2: Agentic Planning Write-Up

This document provides a concise overview of how the chatbot's planner and controller system works.

## The Agentic Loop: How the Bot Decides

The chatbot decides its next action using a "planner/controller" loop powered by LangChain's Agent framework. This system breaks down the complex task of conversation into a simple, repeated cycle: **Reason -> Act -> Observe**.

### Core Components

The decision-making process relies on a few key components working together:

1.  **The LLM (The Brain):** An OpenAI model (`gpt-3.5-turbo`) that does all the reasoning. It reads the user's question, the conversation history, and the list of available tools to understand the user's intent.

2.  **The Tools (The Abilities):** A list of functions the agent can use to get information it doesn't know. Our agent has three tools:
    *   **`Calculator`:** For solving math problems.
    *   **`ZUS_Product_Knowledge_Base`:** For answering questions about ZUS drinkware products via a RAG API.
    *   **`ZUS_Outlet_Information`:** For looking up store details via a Text-to-SQL API.

3.  **The Prompt (The Instructions):** A set of instructions that tells the LLM its goal, what tools it has, and how to use them. The LLM's decision-making is heavily guided by the **description** provided for each tool.

4.  **The Agent Executor (The Engine):** This is the main loop that orchestrates the entire process from start to finish.

### The Three Phases of a Turn

When a user asks a question, the `AgentExecutor` runs through the following phases:

#### 1. Parse Intent (Reason)

The LLM analyzes the user's input in the context of the conversation history. It determines what the user is trying to achieve. For example, it recognizes "what is 5 * 10?" as a math task, and "tell me about your tumblers" as a product information request.

#### 2. Choose an Action (Act)

Based on the parsed intent, the LLM makes a choice:

*   **Use a Tool:** If the user's query matches a tool's description (e.g., asking about math triggers the `Calculator`), the LLM decides to invoke that tool.
*   **Respond Directly:** If no tool is relevant (e.g., for "hello" or "thank you"), or if a tool has already provided the necessary information, the LLM decides to generate a final answer for the user.
*   **Ask a Follow-up Question:** If the user's query is ambiguous (e.g., "tell me about the outlet"), the LLM will respond directly by asking for clarification ("Which outlet are you referring to?").

#### 3. Execute and Observe (Observe)

*   If a tool was chosen, the `AgentExecutor` runs the corresponding Python function.
*   The result of that function—whether it's a successful answer or a handled error message—is captured as an **Observation**.
*   This Observation is fed back to the LLM. The loop then repeats, allowing the LLM to reason based on this new information until it has a final answer for the user. This iterative process is what allows the agent to handle multi-step tasks and recover from tool errors gracefully.