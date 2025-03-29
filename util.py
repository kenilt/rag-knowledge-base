BASE_NAME = "doodoo_base"


def chunk_text(text, target_chunk_size=1000, overlap_size=100):
    """
    Splits a text into chunks by paragraphs, ensuring each chunk has around target_chunk_size words.

    :param text: The full document text
    :param target_chunk_size: Approximate number of words per chunk
    :return: List of text chunks
    """
    paragraphs = text.split("\n")  # Split text into paragraphs
    chunks = []
    current_chunk = []
    current_word_count = 0

    for paragraph in paragraphs:
        paragraph_word_count = len(paragraph.split())
        if current_word_count + paragraph_word_count <= target_chunk_size:
            current_chunk.append(paragraph)
            current_word_count += paragraph_word_count
        else:
            # Add the current chunk to the list and start a new chunk
            if current_chunk:
                chunks.append("\n".join(current_chunk))

            overlap_words = " ".join(current_chunk).split()[-overlap_size:]
            current_chunk = [" ".join(overlap_words), paragraph]
            current_word_count = len(overlap_words) + paragraph_word_count

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


def print_error(content):
    print(f"\033[31m{content}\033[0m")
