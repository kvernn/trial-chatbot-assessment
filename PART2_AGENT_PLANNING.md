Part 2: Agentic Planning Write-Up

This document details how the chatbot's planner/controller system functions, as required by Part 2 of the assessment. The system is built using LangChain's Agent framework, which provides a robust loop for decision-making and action execution.
Objective: The Decision-Making Loop

The core objective is to show how the bot decides its next action. Our implementation, centered around the AgentExecutor, accomplishes this by performing a continuous loop that can be broken down into the three key phases requested in the assessment:

    Parsing Intent and Missing Information

    Choosing an Action

    Executing the Action and Returning the Result

Core Components of the Planner/Controller

Before detailing the phases, it's important to understand the components that constitute our "planner/controller code" (app/chatbot.py):

    LLM (ChatOpenAI): The core reasoning engine. It's the "brain" that does the actual parsing and deciding.

    Tools (tools list): A list of capabilities the agent can use. Currently, this includes the Calculator tool. The description of each tool is critical, as the LLM uses it to determine relevance.

    Memory (ConversationBufferMemory): Stores the history of the conversation. This provides essential context for the LLM to understand follow-up questions and user intent over multiple turns.

    Prompt (AGENT_PROMPT): A carefully crafted set of instructions that guides the LLM. It tells the agent its persona, how to think, what tools it has access to, and where to find the conversation history and its own internal thoughts (the "scratchpad").

    Agent Logic (create_openai_tools_agent): This creates the agent's logic, specifically designed to leverage the native tool-calling ability of modern OpenAI models.

    Agent Executor (AgentExecutor): This is the runtime that orchestrates the entire loop. It takes user input, invokes the agent, executes tool calls, and manages the flow of information.

Phase 1: Parsing Intent and Missing Information

This phase is primarily handled by the LLM based on the information provided to it by the AgentExecutor.

    Input Synthesis: For every turn, the LLM receives a comprehensive package of information structured by the AGENT_PROMPT. This includes:

        The user's latest message ({input}).

        The full conversation history (chat_history).

        The descriptions of all available tools.

    Intent Inference: The LLM synthesizes this information to understand the user's goal.

        If the user asks, "What is 15 * 25?", the LLM identifies a clear mathematical intent.

        If the user asks, "What about that outlet in SS2?", the LLM uses the chat_history to infer that "that outlet" refers to a previously discussed topic, thus correctly parsing the intent of a follow-up question.

    Handling Missing Information: If information is missing, the LLM can decide to ask a clarifying question. This is a form of choosing the "respond directly" action, where the response itself is the follow-up question.

Phase 2: Choosing an Action

Once the LLM has parsed the intent, it chooses one of the following actions:

    Invoke a Tool (e.g., Calculator):

        Trigger: The user's query strongly matches a tool's description.

        Mechanism: The LLM, using its native tool-calling ability, generates a structured output indicating which tool to call (Calculator) and what arguments to pass (e.g., the expression 15 * 25).

        Example: For "Calculate 100/4", the LLM chooses to Invoke: Calculator with the input 100/4.

    Respond Directly to the User (Finish):

        Trigger: The user's query does not match any tool's description, or a tool has already provided all the necessary information for a final answer.

        Mechanism: The LLM generates a natural language response intended for the user.

        Example: For "What's your name?", the LLM finds no relevant tool and chooses to respond directly with "I am an AI assistant...".

    Ask a Follow-Up Question:

        This is a sub-type of "Respond Directly." The LLM formulates a question to gather more information from the user before it can proceed.

Phase 3: Executing the Action and Returning the Result

This phase is managed by the AgentExecutor.

    If the chosen action is a TOOL CALL:

        The AgentExecutor receives the tool name and arguments from the LLM.

        It executes the corresponding Python function (e.g., safe_calculator_run).

        The return value from the function becomes the Observation.

        Crucially, this Observation is not the final answer. It is added to the agent_scratchpad and the loop repeats from Phase 1. The LLM now sees the tool's result and decides its next action, which is often to formulate a final answer to the user.

        This loop is how our agent handles tool errors gracefully. The safe_calculator_run returns an error message as the Observation, and the LLM then formulates a polite, user-friendly response based on that error message.

    If the chosen action is to RESPOND DIRECTLY:

        The AgentExecutor recognizes this as the "Finish" state.

        It stops the loop and returns the LLM's generated text as the final output of the chain. This is the response the user sees.

This iterative process of Thought (LLM) → Action (Tool/Response) → Observation (Tool Result) allows the agent to handle complex, multi-step tasks and interact with its tools effectively before presenting a final, coherent answer to the user. The same framework will be used to integrate the more advanced RAG and Text2SQL tools in Part 4.