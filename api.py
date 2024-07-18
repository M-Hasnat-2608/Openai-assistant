from flask import Flask, request, jsonify
import openai
import time
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

open_api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Initialize the OpenAI client
client = openai.Client(api_key=open_api_key)

# Create a new thread and store the thread ID
initial_message = "Hello chat"
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": initial_message,
        }
    ]
)
thread_id = thread.id

def send_message(message_content):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_content
    )
    
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=ASSISTANT_ID)
    
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        time.sleep(1)
    
    message_response = client.beta.threads.messages.list(thread_id=thread_id)
    messages = message_response.data
    latest_message = messages[0]  # Get the latest message
    return latest_message.content[0].text.value

@app.route('/api', methods=['GET'])
def returnResponse():
    input_prompt = request.args.get('query')
    if not input_prompt:
        return jsonify({"error": "No query parameter provided"}), 400
    
    response = send_message(input_prompt)
    return jsonify({'output': response})

if __name__ == "__main__":
    app.run(debug=True)
