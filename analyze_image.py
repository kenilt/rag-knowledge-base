import ollama
import base64


# Convert the image to a Base64-encoded string
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Load and encode the image
image_path = (
    "/Users/thangnguyen/Downloads/DooDoo Files/H2.png"  # Replace with your image path
)
image_base64 = encode_image(image_path)

# Prompt to the model
prompt = "Describe the image content **without any introduction or conclusion**."

# Call Ollama with text + image input
stream = ollama.generate(
    model="gemma3:4b", prompt=prompt, images=[image_path], stream=True
)
for chunk in stream:
    print(chunk["response"], end="", flush=True)
