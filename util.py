BASE_NAME = "brand_base"


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
                chunks.append("\n".join(current_chunk).strip())

            # Handle overlap with multiple paragraphs
            overlap_paragraphs = []
            overlap_word_count = 0
            for prev_paragraph in reversed(current_chunk):
                prev_paragraph_word_count = len(prev_paragraph.split())
                if overlap_word_count + prev_paragraph_word_count > overlap_size:
                    # Cut the last paragraph if it exceeds overlap_size
                    if overlap_word_count == 0:
                        remaining_words = overlap_size - overlap_word_count
                        if remaining_words > 0:
                            truncated_paragraph = " ".join(
                                prev_paragraph.split()[-remaining_words:]
                            )
                            overlap_paragraphs.insert(0, truncated_paragraph)
                    break
                overlap_paragraphs.insert(0, prev_paragraph)
                overlap_word_count += prev_paragraph_word_count

            # Start a new chunk with the overlap and the current paragraph
            current_chunk = overlap_paragraphs + [paragraph]
            current_word_count = overlap_word_count + paragraph_word_count

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append("\n".join(current_chunk).strip())

    return chunks


def print_error(content):
    print(f"\033[31m{content}\033[0m")
