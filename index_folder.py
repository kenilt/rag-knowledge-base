import os
import traceback
import ollama
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
from docx import Document
from pptx import Presentation

from marqo_helper import index_content_to_marqo, search_documents
from util import print_error

INPUT_LENGTH_LIMIT = 450000  # Around 100.000 tokens


# Read TXT
def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# Read DOCX
def read_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


# Read PDF
def read_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(
            page.extract_text() for page in pdf.pages if page.extract_text()
        )
        return text


# Read PPTX
def read_pptx(file_path):
    ppt = Presentation(file_path)
    text = "\n".join(
        [
            shape.text.translate({i: None for i in range(0x00, 0x10)})
            for slide in ppt.slides
            for shape in slide.shapes
            if hasattr(shape, "text")
        ]
    )
    return text


# Read Excel
def read_excel(file_path):
    df = pd.read_excel(file_path, engine="openpyxl")
    data_text = "\n".join([str(row) for row in df.to_dict(orient="records")])
    if len(data_text) > INPUT_LENGTH_LIMIT:
        data_text = data_text[:INPUT_LENGTH_LIMIT]
    prompt = f"Directly extract a summary and relevant insights from the data below. Do not include any preamble or introductory sentences.\n\n{data_text}"

    # Call Ollama with text + image input
    result = ollama.generate(model="gemma3:4b", prompt=prompt)
    text = result["response"]
    print(text)
    return text


# Read image using Gemma 3
def read_image(file_path):
    prompt = "Describe the image content **without any introduction or conclusion**. Provide only the extracted details."
    result = ollama.generate(model="gemma3:4b", prompt=prompt, images=[file_path])
    text = result["response"]
    print(text)
    return text


def index_folder(folder_path):

    for dirpath, _, filenames in os.walk(folder_path):
        for file in filenames:
            if file.startswith("."):
                continue
            file_path = os.path.join(dirpath, file)
            file_ext = file.split(".")[-1].lower()
            print(f"Indexing {file_path}")

            file_content = ""
            try:
                if file_ext == "txt":
                    file_content = read_txt(file_path)
                # elif file_ext == "docx":
                #     file_content = read_docx(file_path)
                # elif file_ext == "pdf":
                #     file_content = read_pdf(file_path)
                # elif file_ext == "pptx":
                #     file_content = read_pptx(file_path)
                elif file_ext == "xlsx":
                    file_content = read_excel(file_path)
                # elif file_ext in ["jpg", "png", "jpeg"]:
                #     file_content = read_image(file_path)
            except Exception as ex:
                print_error(ex)
                traceback.print_exc()
                continue

            if file_content:
                index_content_to_marqo(
                    title=file,
                    content=file_content,
                    file_type=file_ext,
                    url=file_path,
                )


folder_path = "/Users/thangnguyen/Downloads/DooDoo Files"
index_folder(folder_path)

# print(search_documents("What is DooDoo"))
