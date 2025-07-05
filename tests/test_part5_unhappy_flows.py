# tests/test_part5_unhappy_flows.py
import sys
import os
import pytest
import requests

# For adding the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.chatbot import agent_executor

# Testing API directly for the SQL injection test
from fastapi.testclient import TestClient
from api.main import app as fastapi_app

client = TestClient(fastapi_app)

# --- Test Case 1: Missing Parameters ---
def test_missing_parameters_for_outlets():
    """
    Tests how the agent handles a vague request that lacks necessary parameters.
    The agent should ask a clarifying question rather than calling a tool with empty args.
    """

    user_input = "Tell me about outlets"

    response = agent_executor.invoke({"input": user_input, "chat_history": []})
    
    # Assert the agent to asks for clarification
    output = response['output'].lower()
    print(f"\nResponse for missing parameters: {output}")
    assert "which outlet" in output or "what would you like to know" in output or "where" in output or "specific" in output


# --- Test Case 2: API Downtime ---
def test_api_downtime_for_products(mocker):
    """
    Tests graceful failure when the product API is down.
    We use pytest-mock's `mocker` to simulate a requests.exceptions.ConnectionError.
    """

    mocker.patch(
        'requests.get', 
        side_effect=requests.exceptions.ConnectionError("Failed to establish a new connection")
    )
    
    user_input = "Tell me about the ZUS All-Can Tumbler"
    
    # Invoking the agent
    response = agent_executor.invoke({"input": user_input, "chat_history": []})

    output = response['output']
    print(f"\nResponse for API downtime: {output}")
    # Checking for keywords to indicate if LLM understood the connection issue
    assert "apologize" in output.lower() or "issue connecting" in output.lower() or "could not connect" in output.lower() or "knowledge base" in output.lower()


# --- Test Case 3: Malicious Payload (SQL Injection) ---
def test_sql_injection_on_outlets_api():
    """
    Tests the /outlets API directly to see how it handles a SQL injection attempt.
    The Text-to-SQL chain should either ignore the malicious part or the DB driver should prevent it.
    We do NOT want to see a list of all table names.
    """

    malicious_query = "Find outlets in KL; SELECT name FROM sqlite_master WHERE type='table';"
    
    #
    response = client.get(f"/outlets?query={malicious_query}")
    
    # Check 1: Request should not fail with a server error
    assert response.status_code == 200
    
    # Check 2: Response should NOT contain sensitive schema info like 'outlets' or 'sqlite_master'
    response_data = response.json()
    results = response_data.get('results', '').lower()
    sql_query_generated = response_data.get('sql_query', '').lower()

    print(f"\nResponse for SQL injection attempt: {response_data}")
    
    # Assert the malicious part of the query was ignored or neutralized
    assert "sqlite_master" not in sql_query_generated
    assert "union" not in sql_query_generated
    
    # Results should be about outlets in KL, not a list of table names
    assert "mid valley" in results or "suria klcc" in results
    assert "outlets" not in results