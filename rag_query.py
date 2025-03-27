import marqo
from ollama import Client
import readline

from common import BASE_NAME

mq = marqo.Client()
ollama_client = Client()


def distinct_paths(paths):
    seen = set()
    return [x for x in paths if x not in seen and not seen.add(x)]


while True:
    prompt = input(">> ")
    if prompt == "/exit":
        break

    # Retrieve relevant documents
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
        distinct_paths([result["file_path"] for result in results["hits"]])
    )

    # Prepare prompt for Gemma 3 4B
    prompt = f"Context: {context}\n\nQuestion: {prompt}"
    print(prompt)

    print("\n")
    print(f"References:\n{paths}\n\n")
