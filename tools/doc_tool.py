import PyPDF2
import pytesseract
from PIL import Image
import docx


def read_pdf(file_path: str) -> str:
    text = ""

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""

    return text.strip()


def read_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def process_image(file_path: str) -> dict:
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)

        if text.strip():
            return {
                "status": "success",
                "type": "image_text",
                "content": text
            }
        else:
            return {
                "status": "success",
                "type": "image",
                "message": "No readable text found. Please describe the image."
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def process_document(file_path: str) -> dict:
    try:
        if file_path.endswith(".pdf"):
            text = read_pdf(file_path)

            if len(text.strip()) < 50:
                return {
                    "status": "success",
                    "type": "pdf_ocr_required",
                    "message": "PDF may require OCR"
                }

            return {
                "status": "success",
                "type": "pdf",
                "content": text
            }

        elif file_path.endswith(".docx"):
            return {
                "status": "success",
                "type": "docx",
                "content": read_docx(file_path)
            }

        elif file_path.endswith((".png", ".jpg", ".jpeg")):
            return process_image(file_path)

        else:
            return {
                "status": "error",
                "message": "Unsupported file type"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }