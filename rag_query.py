import marqo
from ollama import Client
import readline

from util import BASE_NAME

TOP_K = 5

mq = marqo.Client()
ollama_client = Client()


def distinct_paths(paths):
    seen = set()
    return [x for x in paths if x not in seen and not seen.add(x)]


def retrieve_context_from_marqo(question):
    """Retrieve relevant documents and construct context and paths."""
    results = mq.index(BASE_NAME).search(
        question,
        limit=TOP_K,
        filter_string="file_type:(txt) OR file_type:(pptx) OR file_type:(pdf) OR file_type:(docx) OR file_type:(web)",
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


while True:
    prompt = input(">> ")
    if prompt == "/exit":
        break

    # Retrieve relevant documents
    results = mq.index(BASE_NAME).search(prompt, limit=10)

    # Construct context from retrieved documents
    context = retrieve_context_from_marqo(prompt)
    paths = retrieve_related_documents_from_marqo(prompt)

    # Prepare prompt for Gemma 3 4B
    prompt = f"Retrieved Context: {context}\n\nQuestion: {prompt}"
    print(prompt)

    print("\n")
    print(f"References:\n{paths}\n\n")
