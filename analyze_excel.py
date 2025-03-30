import ollama
import pandas as pd


def read_excel(file_path):
    df = pd.read_excel(file_path, engine="openpyxl")
    return "\n".join([str(row) for row in df.to_dict(orient="records")])


file_path = "/Users/thangnguyen/Downloads/DooDoo Files/Doodoo Mastersheet.xlsx"
data = read_excel(file_path)

# Prompt to the model
prompt = f"Directly extract a summary and relevant insights from the data below. Do not include any preamble or introductory sentences.\n\n{data}"
print(prompt)

# Call Ollama with text + image input
stream = ollama.generate(model="gemma3:4b", prompt=prompt, stream=True)
for chunk in stream:
    print(chunk["response"], end="", flush=True)
