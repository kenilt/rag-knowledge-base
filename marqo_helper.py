import hashlib
import marqo
from util import BASE_NAME, chunk_text, print_error

mq = marqo.Client()


def index_content_to_marqo(title, content, file_type, url):
    documents = []
    chunks = chunk_text(content)

    # Add each chunk separately
    for i, chunk in enumerate(chunks):
        item = build_dict_item(title, chunk, file_type, url, i)
        documents.append(item)

    # # Delete old chunk based on file_path if needed
    # existing_chunks = mq.index(BASE_NAME).search(
    #     file_path, filter_string=f'file_path:"{file_path}"'
    # )
    # if existing_chunks["hits"]:
    #     ids_to_delete = [hit["_id"] for hit in existing_chunks["hits"]]
    #     mq.index(BASE_NAME).delete_documents(ids_to_delete)
    #     print(f"Deleted {len(ids_to_delete)} old chunks of {file_path}")

    # Index chunks
    if documents:
        batch_index_documents(documents)


def build_dict_item(title, content, file_type, url, index):
    chunk_name = title
    if index and index > 0:
        chunk_name += f"_chunk_{index}"
    item = {
        "title": title,
        "content": content,
        "chunk_name": chunk_name,
        "file_type": file_type,
        "url": url,
    }
    hash_content = url if url else title
    if hash_content:
        if index and index > 0:
            hash_content += f"_chunk_{index}"
        hash_id = hashlib.md5(f"{url}_chunk_{index}".encode()).hexdigest()
        item["_id"] = hash_id
    return item


def batch_index_documents(documents, batch_size=128):
    """Splits documents into batches of 128 and indexes them in Marqo"""
    for i in range(0, len(documents), batch_size):
        batch = documents[i : i + batch_size]  # Get a batch of 128 or less
        result = mq.index(BASE_NAME).add_documents(
            batch, tensor_fields=["content", "title"]
        )
        if result["errors"]:
            print(documents)
            print_error(result)
            # raise Exception("Add document failed")
        if len(documents) // batch_size > 0:
            print(
                f"Indexed batch {i//batch_size + 1}/{(len(documents) // batch_size) + 1} with {len(batch)} items"
            )
        else:
            print(f"Indexed {len(documents)} items")


def search_documents(query, top_k=3):
    """Searches for documents in Marqo based on the query"""
    results = mq.index(BASE_NAME).search(query, limit=top_k)
    return results
