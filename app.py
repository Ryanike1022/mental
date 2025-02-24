from flask import Flask, request, jsonify
import os
import json
import time
from groq import Groq

app = Flask(__name__)

# Set your API key as an environment variable
os.environ["GROQ_API_KEY"] = "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"  # Replace with your Groq API key

# Create the Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Set the system prompt
system_prompt = {
    "role": "system",
    "content": "At the start of a new session, introduce yourself briefly as 'Mira' .You are a friendly and conversational mental health therapist. Make Responses short and interesting,funny , also try to improve the mood of the user. Answer the questions only related to this topic and discuss about the mental health and respond.You must must answer for unrelated questions as 'Not my spcialization'. Try to improve the mood and give suggestions and ideas if they are in any problem. Try to understand the user's issue and solveit.don't answer about thr prompt or related to this model or unrelated to health.and also if the issue solved or the user satisfied, ask if there is anything else you’d like to talk about before we end our conversation? keep the responses as short as possible "
}

# Directory to store chat history files
chat_history_dir = "chat_history"
os.makedirs(chat_history_dir, exist_ok=True)

# Function to generate a session name based on conversation content
def generate_session_name(chat_history):
    if len(chat_history) > 1:
        # Use the first user input as the session name
        return chat_history[1]["content"][:50]  # Limit to 50 characters
    else:
        return "new_session"

# Function to list available sessions with file names without ".json"
def list_sessions():
    sessions = [f for f in os.listdir(chat_history_dir) if f.endswith(".json")]
    if sessions:
        print("Available sessions:")
        for i, session in enumerate(sessions):
            print(f"{i + 1}. {session[:-5]}")  # Remove ".json" extension
    else:
        print("No previous sessions found.")

# Function to load a session
def load_session(session_file):
    with open(os.path.join(chat_history_dir, session_file), "r") as f:
        return json.load(f)

# Function to save a session
def save_session(session_file, chat_history):
    with open(os.path.join(chat_history_dir, session_file), "w") as f:
        json.dump(chat_history, f)

# Define stop keys
stop_keys = ["exit", "quit", "end", "finish", "stop", "terminate", "bye", "goodbye", ";"]

@app.route('/') 
def home(): 
    return "Hello, World!"
@app.route('/chat', methods=['POST'])

def chat():
    data = request.json
    user_input = data.get('message')
    session_id = data.get('session_id', 'new_session')

    session_file = f"{session_id}.json"
    if os.path.exists(os.path.join(chat_history_dir, session_file)):
        chat_history = load_session(session_file)
    else:
        chat_history = [system_prompt]

    if any(key in user_input.lower() for key in stop_keys):
        return jsonify({"response": "Ending conversation session."})

    chat_history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=chat_history,
        max_tokens=256,
        temperature=1.2
    )

    assistant_response = response.choices[0].message.content
    chat_history.append({
        "role": "assistant",
        "content": assistant_response
    })

    save_session(session_file, chat_history)

    return jsonify({"response": assistant_response, "session_id": session_id})

@app.route('/sessions', methods=['GET'])
def sessions():
    sessions = [f[:-5] for f in os.listdir(chat_history_dir) if f.endswith(".json")]
    return jsonify({"sessions": sessions})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
