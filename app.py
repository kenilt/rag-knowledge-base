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

from util import BASE_NAME

load_dotenv()

# SlackApp
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
app = App(token=SLACK_BOT_TOKEN)

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Marqo and Ollama
mq = marqo.Client()
ollama_client = Client()

# Constants
TOP_K = 5
INACTIVITY_TIMEOUT = 3600  # 1 hour in seconds
INPUT_TOKEN_LIMIT = 50000
SLACK_MESSAGE_LIMIT = 3000

conversation_histories = {}
last_activity = {}  # Store last activity timestamps

# Dictionary to store buffers and control flags for each request
buffers = {}
stop_flags = {}


def clear_inactive_chats():
    while True:
        now = time.time()
        chats_to_clear = [
            key
            for key, last_time in last_activity.items()
            if now - last_time > INACTIVITY_TIMEOUT
        ]
        for key in chats_to_clear:
            if key in conversation_histories:
                del conversation_histories[key]
                del last_activity[key]
                print(f"Cleared chat history for {key} due to inactivity.")
        time.sleep(60)  # Check every minute


threading.Thread(target=clear_inactive_chats, daemon=True).start()


def summarize_conversation(history):
    prompt = "Summarize the following conversation:\n"
    for message in history:
        prompt += f"{message['user']}: {message['text']}\n"
    try:
        summary_response = model.generate_content(prompt)
        return summary_response.text
    except Exception as e:
        print(f"Error summarizing: {e}")
        return None


def is_reach_token_limit(history):
    total_tokens = 0
    for message in history:
        total_tokens += len(message["text"].split())
    if total_tokens >= INPUT_TOKEN_LIMIT:
        return True
    return False


def build_prompt(history, context, current_message):
    prompt = "Conversation History:\n"
    for message in history:
        prompt += f"{message['role']}: {message['text']}\n"
    if context:
        prompt += "\nRetrieved Context:\n"
        prompt += context
    prompt += f"\nUser: {current_message}\nBot:"
    return prompt


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
        time.sleep(1)
        if buffers[request_id]:
            if is_thinking:
                is_thinking = False
            message = format_message(buffers[request_id]) + "..."
        elif is_thinking:
            message += "🤔"

        if len(message) < SLACK_MESSAGE_LIMIT:
            update_response_func(message)


def generate_ai_response(
    question, conversation_key, update_response_func, trailing_response_func
):
    request_id = str(time.time())

    context = retrieve_context_from_marqo(question)
    history: list = get_conversation_history(conversation_key)

    # Prepare prompt with retrieved context
    prompt = build_prompt(history, context, question)
    print(prompt)

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
        paths = retrieve_related_documents_from_marqo(question)
        message = format_message(buffers[request_id]) + f"\n\n*References:*\n{paths}"
        chunks = chunk_message(message)
        if len(chunks) >= 1:
            update_response_func(chunks[0])
            for chunk in chunks[1:]:
                trailing_response_func(chunk)
        print(message)

    track_converstion_history(history, question, buffers[request_id])

    # Clean up the request from the dictionary
    del buffers[request_id]
    del stop_flags[request_id]

    summarize_history_if_needed(history, conversation_key)


def retrieve_context_from_marqo(question):
    """Retrieve relevant documents and construct context and paths."""
    results = mq.index(BASE_NAME).search(
        question,
        limit=TOP_K,
        # filter_string="file_type:(txt) OR file_type:(pptx) OR file_type:(pdf) OR file_type:(docx) OR file_type:(web)",
    )
    context = " ".join([result["content"] for result in results["hits"]])
    return context


def retrieve_related_documents_from_marqo(question):
    results = mq.index(BASE_NAME).search(question, limit=3 * TOP_K)
    references = ", ".join(
        distinct_paths(
            [f"<{get_hit_url(result)}|{result['title']}>" for result in results["hits"]]
        )
    )
    return references


def get_hit_url(result):
    url = result["url"]
    if url and url.startswith("http"):
        return url
    else:
        return "http://localhost"  # Default URL if not provided


def get_conversation_history(conversation_key):
    """Initialize or retrieve the conversation history for a given key."""
    if conversation_key not in conversation_histories:
        conversation_histories[conversation_key] = []
    return conversation_histories[conversation_key]


def track_converstion_history(history: list, question, answer):
    history.append({"role": "User", "text": question})
    history.append({"role": "Bot", "text": answer})
    # Basic token management (limit to last 10 messages)
    if len(history) > 20:
        history = history[-20:]


def summarize_history_if_needed(history, conversation_key):
    if not is_reach_token_limit(history):
        return
    summary = summarize_conversation(history)
    if summary:
        conversation_histories[conversation_key] = [
            {
                "user": "Bot",
                "text": f"Conversation summarized. Continuing from summary:\n{summary}",
            }
        ]
        print(f"Conversation summarized. Continuing from summary:\n{summary}")
    else:
        print(
            "Token limit reached, but summarization failed. Continuing without summary."
        )


def generate_response_by_gemma3(prompt, request_id):
    # Need to set up ollama first, then pull some models
    stream = ollama_client.generate(model="gemma3:4b", prompt=prompt, stream=True)
    for chunk in stream:
        buffers[request_id] += chunk["response"]  # Append response to buffer


def generate_response_by_gemini(prompt, request_id):
    try:
        response_stream = model.generate_content(prompt, stream=True)
        for chunk in response_stream:
            buffers[request_id] += chunk.text  # Append response to buffer

    except Exception as e:
        print(f"An error occurred: {e}")


@app.event("message")
def handle_message(event, say, client: WebClient):
    user_message = event["text"]
    thread_ts = event.get("thread_ts") or event["ts"]
    channel_type = event.get("channel_type")
    channel_id = event["channel"]
    user_id = event["user"]
    conversation_key = f"{channel_id}-{user_id}"

    print(f">> {user_id} >>", user_message)

    # Update last activity timestamp
    last_activity[conversation_key] = time.time()

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

    generate_ai_response(
        user_message, conversation_key, update_response_func, trailing_response_func
    )


if __name__ == "__main__":
    # Run bolt over socket mode
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
