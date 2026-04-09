import requests
import base64

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "gemma4:e2b"


def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def encode_image_bytes(image_bytes: bytes):
    return base64.b64encode(image_bytes).decode("utf-8")


def generate(
    prompt: str,
    model: str = None,
    image_path: str = None,
    image_paths: list[str] = None,
    image_bytes_list: list[bytes] = None,
) -> str:

    selected_model = model if model else MODEL

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False
    }

    image_list = []
    if image_path:
        image_paths = [image_path]

    if image_paths:
        for path in image_paths:
            try:
                image_list.append(encode_image(path))
            except Exception as e:
                return f"Image encoding error: {e}"

    if image_bytes_list:
        for image_bytes in image_bytes_list:
            try:
                image_list.append(encode_image_bytes(image_bytes))
            except Exception as e:
                return f"Image encoding error: {e}"

    if image_list:
        payload["images"] = image_list

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        return data.get("response", "").strip()

    except Exception as e:
        return f"LLM Error: {e}"