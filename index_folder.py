import os
import traceback
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
from docx import Document
from pptx import Presentation

from marqo_helper import index_content_to_marqo, search_documents
from util import print_error


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
            shape.text
            for slide in ppt.slides
            for shape in slide.shapes
            if hasattr(shape, "text")
        ]
    )
    return text


# Read Excel
def read_excel(file_path):
    df = pd.read_excel(file_path, engine="openpyxl")
    return "\n".join([str(row) for row in df.to_dict(orient="records")])


# Extract Text from Images (OCR)
def read_image(file_path):
    image = Image.open(file_path)
    text = "".join(pytesseract.image_to_string(image))
    print(text)
    return text


def index_folder(folder_path):

    for dirpath, _, filenames in os.walk(folder_path):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            file_ext = file.split(".")[-1].lower()
            print(f"Indexing {file_path}")

            file_content = ""
            try:
                if file_ext == "txt":
                    file_content = read_txt(file_path)
                elif file_ext == "docx":
                    file_content = read_docx(file_path)
                elif file_ext == "pdf":
                    file_content = read_pdf(file_path)
                elif file_ext == "pptx":
                    file_content = read_pptx(file_path)
                elif file_ext == "xlsx":
                    file_content = read_excel(file_path)
                elif file_ext in ["jpg", "png", "jpeg"]:
                    file_content = read_image(file_path)  # OCR extraction
            except Exception as ex:
                print_error(ex)
                traceback.print_exc()
                continue

            index_content_to_marqo(
                title=file,
                content=file_content,
                file_type=file_ext,
                url=file_path,
            )


folder_path = "/Users/thangnguyen/Downloads/DooDoo Files"
index_folder(folder_path)

print(search_documents("What is DooDoo"))
