from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json

# Add this to your existing api/main.py

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ZUS Coffee Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            #chat-container { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 10px; }
            #user-input { width: 70%; padding: 10px; }
            #send-btn { width: 25%; padding: 10px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background-color: #e3f2fd; text-align: right; }
            .bot { background-color: #f5f5f5; }
        </style>
    </head>
    <body>
        <h1>ZUS Coffee Assistant</h1>
        <div id="chat-container"></div>
        <input type="text" id="user-input" placeholder="Ask about products, outlets, or calculations...">
        <button id="send-btn" onclick="sendMessage()">Send</button>

        <script>
            async function sendMessage() {
                const input = document.getElementById('user-input');
                const message = input.value;
                if (!message) return;

                // Display user message
                addMessage(message, 'user');
                input.value = '';

                // Send to chatbot endpoint
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: message})
                    });
                    const data = await response.json();
                    addMessage(data.response, 'bot');
                } catch (error) {
                    addMessage('Sorry, an error occurred.', 'bot');
                }
            }

            function addMessage(message, sender) {
                const chatContainer = document.getElementById('chat-container');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + sender;
                messageDiv.textContent = message;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            document.getElementById('user-input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    # Use your existing agent_executor here
    # For now, returning a simple response
    response = agent_executor.invoke({"input": user_message})

    return {"response": response['output']}