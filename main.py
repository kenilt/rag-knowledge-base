import marqo
from ollama import Client

from common import BASE_NAME

mq = marqo.Client()
ollama_client = Client()


# def rag_query(user_query, top_k=3):
#     # Retrieve relevant documents
#     results = mq.index(BASE_NAME).search(user_query, limit=top_k)

#     # Construct context from retrieved documents
#     context = " ".join([result["content"] for result in results["hits"]])
#     # paths = ", ".join([result["file_path"] for result in results["hits"]])

#     # Prepare prompt for Gemma 3 4B
#     prompt = f"Context: {context}\n\nQuestion: {user_query}\n\nAnswer:"
#     print(prompt)

#     # Generate response using Gemma 3 4B
#     response = ollama_client.generate(model="gemma3:4b", prompt=prompt)

#     return response["response"]


def distinct_paths(paths):
    seen = set()
    return [x for x in paths if x not in seen and not seen.add(x)]


# Example usage
# query = "What is DooDoo?"
# answer = rag_query(query)
# print("===> Answer:", answer)


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
    prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer:"

    print("...")
    stream = ollama_client.generate(model="gemma3:4b", prompt=prompt, stream=True)
    for chunk in stream:
        print(chunk["response"], end="", flush=True)
    print("\n")
    print(f"References:\n{paths}\n\n")
