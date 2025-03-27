# RAG-Based Slack Bot with Marqo and Generative AI

This project implements a Slack bot that uses Retrieval-Augmented Generation (RAG) to answer user queries. It integrates with Marqo for document indexing and retrieval, and uses generative AI models like Gemini and Ollama for generating responses. The bot is built using the Slack Bolt framework and supports real-time interaction in Slack channels.

## Features

- **Slack Integration**: Responds to messages in Slack channels or direct messages.
- **Document Indexing**: Supports indexing of various file types (e.g., `.txt`, `.pdf`, `.docx`, `.pptx`, `.xlsx`, images) using Marqo.
- **Generative AI**: Uses Gemini and Ollama models for generating responses based on retrieved documents.
- **Streaming Responses**: Streams AI-generated responses in real-time.
- **Reference Links**: Provides references to the documents used for generating answers.

## Prerequisites

1. **Python**: Ensure Python 3.8+ is installed.
2. **Ollama**: Download [Ollama](https://github.com/ollama/ollama) Client that can run multiple models  
  Install Ollama then pull a model, ex: `gemma3:4b`
3. **Marqo**: Set up a [Marqo](https://github.com/marqo-ai/marqo) instance for document indexing.
4. **Generative AI APIs** (Optional):
   - Gemini API key (`GEMINI_API_KEY`)
   - Ollama setup for local models.
5. **Slack App** (Optional): Create a Slack app and obtain the following tokens:
   - `SLACK_BOT_TOKEN`
   - `SLACK_APP_TOKEN`

## Installation

1. Clone the repository:
  ```bash
  git clone <repository-url>
  cd rag-test
  ```
   
2. Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
3. Set up the .env file with your credentials (Required for Slack app):
  ```bash
  SLACK_BOT_TOKEN=<your-slack-bot-token>
  SLACK_APP_TOKEN=<your-slack-app-token>
  GEMINI_API_KEY=<your-gemini-api-key>
  ```

## Usage
1. Start the Slack Bot
Run the bot using the following command:
  ```python
  python app.py
  ```
The bot will connect to Slack and start listening for messages.

2. Start the Local AI
Run the local AI using the following command:
  ```python
  python main.py
  ```
3. Index Documents
To index documents, use the index_folder.py script:
  ```python
  python index_folder.py
  ```
Ensure the folder path is correctly set in the script.

3. Query the System
You can query the system using the Slack bot or the command-line tool:
  ```python
  python rag_query.py
  ```
4. Manage the Index
Create a new index:
  ```python
  python create_base.py
  ```
Delete an existing index:
  ```python
  python delete_base.py
  ```

### Supported File Types
- Text files (.txt)
- Word documents (.docx)
- PDFs (.pdf)
- PowerPoint presentations (.pptx)
- Excel files (.xlsx)
- Images (.jpg, .png, .jpeg)


## License
This project is licensed under the MIT License.

## Acknowledgments
- Marqo for document indexing and retrieval.
- Slack Bolt for Slack integration.
- Google Generative AI for AI-powered responses.
- Ollama for local generative AI models.
