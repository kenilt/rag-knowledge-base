import os
from pydoc import text
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import google.generativeai as genai

import threading
import time
import marqo
from ollama import Client
from slack_sdk import WebClient

from common import BASE_NAME

load_dotenv()

# SlackApp
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
app = App(token=SLACK_BOT_TOKEN)

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

SLACK_MESSAGE_LIMIT = 3000


mq = marqo.Client()
ollama_client = Client()

# Dictionary to store buffers and control flags for each request
buffers = {}
stop_flags = {}


def distinct_paths(paths):
    seen = set()
    return [x for x in paths if x not in seen and not seen.add(x)]


def format_message(message):
    return message.replace("**", "*")


def chunk_message(text: str):
    if len(text) <= SLACK_MESSAGE_LIMIT:
        return [text]

    lines = text.split("\n")
    chunks = []
    current_chunk = ""

    for line in lines:
        if (
            len(current_chunk) + len(line) + 1 <= SLACK_MESSAGE_LIMIT
        ):  # +1 for the newline character
            current_chunk += line + "\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())  # Remove trailing newline
            current_chunk = line + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def buffer_worker(request_id, update_response_func):
    """Prints the buffer for a specific request every 3 seconds."""
    global buffers, stop_flags
    is_thinking = True
    message = "Thinking... 🤔"

    while not stop_flags[request_id]:
        time.sleep(2)
        if buffers[request_id]:
            if is_thinking:
                is_thinking = False
            message = format_message(buffers[request_id]) + "..."
        elif is_thinking:
            message += "🤔"

        if len(message) < SLACK_MESSAGE_LIMIT:
            update_response_func(message)


def generate_ai_response(prompt, update_response_func, trailing_response_func):
    request_id = str(time.time())

    # Retrieve relevant documents (Need to set up marqo first, and index some documents)
    results = mq.index(BASE_NAME).search(prompt, limit=10)

    # Construct context from retrieved documents
    context = " ".join(
        [
            result["content"]
            for result in results["hits"]
            if (result["file_type"] in ["txt", "pptx", "pdf", "docx"])
        ][0:3]
    )
    paths = "\n".join(
        distinct_paths(
            [f"<https://example.com|{result["title"]}>" for result in results["hits"]]
        )
    )

    # Prepare prompt for Gemma 3 4B
    prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer:"

    buffers[request_id] = ""  # Create buffer for this request
    stop_flags[request_id] = False  # Control flag for stopping thread

    # Start a separate buffer thread for this request
    buffer_thread = threading.Thread(
        target=buffer_worker, args=(request_id, update_response_func), daemon=True
    )
    buffer_thread.start()

    generate_response_by_gemini(prompt, request_id)

    # Stop the buffer thread after the stream ends
    stop_flags[request_id] = True
    buffer_thread.join()  # Ensure the thread stops before moving forward

    if buffers[request_id]:
        message = format_message(buffers[request_id]) + f"\n\n*References:*\n{paths}"
        chunks = chunk_message(message)
        if len(chunks) >= 1:
            update_response_func(chunks[0])
            for chunk in chunks[1:]:
                trailing_response_func(chunk)

    # Clean up the request from the dictionary
    del buffers[request_id]
    del stop_flags[request_id]


def generate_response_by_gemma3(prompt, request_id):
    # Need to set up ollama first, then pull some models
    stream = ollama_client.generate(model="gemma3:4b", prompt=prompt, stream=True)
    for chunk in stream:
        buffers[request_id] += chunk["response"]  # Append response to buffer


def generate_response_by_gemini(prompt, request_id):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response_stream = model.generate_content(prompt, stream=True)
    for chunk in response_stream:
        buffers[request_id] += chunk.text  # Append response to buffer


@app.event("message")
def handle_message(event, say, client: WebClient):
    user_message = event["text"]
    thread_ts = event.get("thread_ts") or event["ts"]
    channel_type = event.get("channel_type")
    print(">>", user_message)

    # Initial response
    if channel_type == "im":
        initial_response = say(text="Thinking... 🤔")
    else:
        initial_response = say(text="Thinking... 🤔", thread_ts=thread_ts)

    bot_message_ts = initial_response["ts"]  # Get the message timestamp

    def update_response_func(message):
        client.chat_update(
            channel=event["channel"],
            ts=bot_message_ts,  # Update the bot's previous message
            text=message,
        )

    def trailing_response_func(message):
        client.chat_postMessage(channel=event["channel"], text=message)

    generate_ai_response(user_message, update_response_func, trailing_response_func)


if __name__ == "__main__":
    # Run bolt over socket mode
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
