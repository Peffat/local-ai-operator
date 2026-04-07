import requests
import base64

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "gemma4:e2b"


def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def generate(prompt: str, model: str = None, image_path: str = None) -> str:

    selected_model = model if model else MODEL

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False
    }

    # ✅ FIX: Proper image encoding
    if image_path:
        try:
            encoded_image = encode_image(image_path)
            payload["images"] = [encoded_image]
        except Exception as e:
            return f"Image encoding error: {e}"

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        return data.get("response", "").strip()

    except Exception as e:
        return f"LLM Error: {e}"