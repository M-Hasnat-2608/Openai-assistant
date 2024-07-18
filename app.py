from flask import Flask, request, jsonify
import openai
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Function to send message and get response from the thread
def send_message(message_content, thread_id):
    client = openai.Client(api_key=openai.api_key)
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

@app.route('/', methods=['GET'])
def return_response():
    input_prompt = request.args.get('query')
    first_time_or_not = request.args.get('first_time_or_not')
    input_thread_id = request.args.get('thread_id')
    
    if not input_prompt or not first_time_or_not:
        return jsonify({"error": "Missing query or first_time_or_not parameter"}), 400
    
    # Check if the query is the complex key to terminate the thread
    complex_key = "terminate_thread"
    if input_prompt == complex_key:
        # Terminate the thread (Note: OpenAI API might not support thread termination directly, this is a placeholder)
        # Assuming we are just acknowledging the termination
        return jsonify({'output': 'Thread terminated', 'thread_id': input_thread_id})
    
    # If it's the first time, create a new thread
    if first_time_or_not == "1":
        client = openai.Client(api_key=openai.api_key)
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
    else:
        # Use the provided thread ID
        thread_id = input_thread_id

    # Send message and get response
    response = send_message(input_prompt, thread_id)
    
    return jsonify({'output': response, 'thread_id': thread_id})
