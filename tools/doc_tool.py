import PyPDF2
import pytesseract
from PIL import Image, ImageOps
import docx
import pandas as pd
from pdf2image import convert_from_path
import re
import io


def read_pdf(file_path: str) -> str:
    text = ""

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""

    return text.strip()


def ocr_image(img: Image.Image) -> str:
    text = pytesseract.image_to_string(img, lang="eng", config="--psm 6")
    if not text.strip():
        gray = ImageOps.grayscale(img)
        text = pytesseract.image_to_string(gray, lang="eng", config="--psm 6")
    return text.strip()


def ocr_pdf(file_path: str, max_pages: int = 2) -> str:
    text = ""
    try:
        pages = convert_from_path(file_path, dpi=200, first_page=1, last_page=max_pages)
        for page in pages:
            page_text = ocr_image(page)
            text += page_text + "\n"
    except Exception:
        return ""
    return text.strip()


def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "unknown"

    try:
        from langdetect import detect

        return detect(text)
    except Exception:
        normalized = text.lower()
        words = re.findall(r"\w+", normalized)
        if not words:
            return "unknown"

        english_stopwords = {
            "the",
            "and",
            "is",
            "in",
            "to",
            "of",
            "a",
            "that",
            "it",
            "for",
            "on",
            "with",
            "as",
            "this",
            "be",
            "are",
            "or",
            "was",
            "by",
            "an",
        }
        stopword_count = sum(1 for w in words if w in english_stopwords)
        if stopword_count / len(words) >= 0.15:
            return "english"
        if re.search(r"[а-яА-Я]", text):
            return "russian"
        if re.search(r"[\u4e00-\u9fff]", text):
            return "chinese"
        if re.search(r"[áéíóúñçüãõ]", normalized):
            return "spanish"
        if re.search(r"[àâæçéèêëîïôœùûüÿ]", normalized):
            return "french"
        return "unknown"


def should_fallback_to_ocr(text: str) -> bool:
    if not text or not text.strip():
        return True

    normalized = text.strip().lower()
    words = re.findall(r"\w+", normalized)
    if not words:
        return True

    scanner_signatures = [
        "camscanner",
        "scanned by",
        "document scanner",
        "page 1",
        "page 2",
        "share via",
    ]

    # If the extracted text is still very short, it may be a scanned document or metadata-only PDF.
    if len(words) < 20:
        if any(sig in normalized for sig in scanner_signatures):
            return True
        if re.search(r"[.!?]", normalized) and len(set(words)) >= 3:
            return False
        return True

    if any(sig in normalized for sig in scanner_signatures) and len(words) <= 40:
        return True

    unique = set(words)
    if len(unique) <= max(4, len(words) // 10) and len(words) < 60:
        return True

    return False


def read_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_pdf_images_as_bytes(file_path: str, max_pages: int = 2) -> list[bytes]:
    images = []
    try:
        pages = convert_from_path(file_path, dpi=300, first_page=1, last_page=max_pages)
        for page in pages:
            buffer = io.BytesIO()
            page.save(buffer, format="PNG")
            images.append(buffer.getvalue())
    except Exception:
        pass
    return images


def read_spreadsheet(file_path: str) -> dict:
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        columns = list(df.columns.astype(str))
        row_count = len(df)
        preview = df.head(5).to_csv(index=False)

        return {
            "status": "success",
            "type": "spreadsheet",
            "content": preview,
            "metadata": {
                "rows": row_count,
                "columns": len(columns),
                "column_names": columns[:10]
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def process_image(file_path: str) -> dict:
    try:
        img = Image.open(file_path)
        text = ocr_image(img)

        if text.strip():
            return {
                "status": "success",
                "type": "image_text",
                "content": text,
                "language": detect_language(text)
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
        if file_path.lower().endswith(".pdf"):
            text = read_pdf(file_path)
            if text.strip():
                return {
                    "status": "success",
                    "type": "pdf",
                    "content": text,
                    "language": detect_language(text)
                }

            image_bytes_list = extract_pdf_images_as_bytes(file_path)
            if image_bytes_list:
                combined_text = ""
                for image_bytes in image_bytes_list:
                    image = Image.open(io.BytesIO(image_bytes))
                    combined_text += ocr_image(image) + "\n"

                if combined_text.strip():
                    return {
                        "status": "success",
                        "type": "pdf_ocr",
                        "content": combined_text.strip(),
                        "language": detect_language(combined_text),
                        "image_bytes_list": image_bytes_list
                    }

                return {
                    "status": "success",
                    "type": "pdf_image",
                    "content": "This PDF appears to contain image-based pages. No selectable text was extracted.",
                    "language": "unknown",
                    "image_bytes_list": image_bytes_list
                }

            return {
                "status": "success",
                "type": "pdf",
                "content": "",
                "language": "unknown"
            }

        elif file_path.endswith(".docx"):
            text = read_docx(file_path)
            return {
                "status": "success",
                "type": "docx",
                "content": text,
                "language": detect_language(text)
            }

        elif file_path.endswith((".png", ".jpg", ".jpeg")):
            return process_image(file_path)
        elif file_path.endswith(('.csv', '.xlsx', '.xls')):
            return read_spreadsheet(file_path)
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