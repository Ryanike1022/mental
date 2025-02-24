from flask import Flask, request, jsonify
import os
from groq import Groq

app = Flask(__name__)

# Set your API key as an environment variable
os.environ["GROQ_API_KEY"] = "your-api-key"

# Create the Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": user_input}],
        max_tokens=256,
        temperature=1.2
    )
    return jsonify({"response": response.choices[0].message.content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
