import re
from tools.excel_tool import analyze_excel_with_ai
from tools.doc_tool import process_document
from utils.llm_client import generate


def build_prompt_with_history(user_input, history, system_prompt):
    """
    Build a conversational prompt using previous chat history
    """
    conversation = ""

    for msg in history:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            conversation += f"User: {content}\n"
        else:
            conversation += f"Assistant: {content}\n"

    conversation += f"User: {user_input}\nAssistant:"

    return system_prompt + "\n\n" + conversation


def describe_file_context(file_path, file_info):
    if file_info.get("status") != "success":
        return f"The file at {file_path} could not be processed cleanly. {file_info.get('message', 'No details available.')}"

    ftype = file_info.get("type")
    if ftype == "pdf":
        snippet = file_info.get("content", "").strip()
        snippet = snippet[:1500].strip()
        questions = len(re.findall(r"\?", snippet))
        note = "This PDF contains extracted text."
        if questions >= 2:
            note += " It appears to include questions or prompts."
        if len(snippet) > 800:
            note += " It also appears to be a longer document that may need summarization."
        return f"{note}\nExtracted text snippet:\n{snippet}"

    if ftype == "pdf_ocr":
        snippet = file_info.get("content", "").strip()
        snippet = snippet[:1500].strip()
        questions = len(re.findall(r"\?", snippet))
        note = "This PDF appears to be a scanned document or image-based PDF. OCR text has been extracted."
        if file_info.get("language"):
            note += f" Detected language: {file_info.get('language')}."
        if questions >= 2:
            note += " It appears to include questions or prompts."
        if len(snippet) > 800:
            note += " It also appears to be a longer document that may need summarization."
        return f"{note}\nOCR extracted text snippet:\n{snippet}"

    if ftype == "docx":
        snippet = file_info.get("content", "").strip()[:1500]
        note = "This Word document contains text."
        if len(snippet) > 800:
            note += " It may include an article, report, or long narrative that can be summarized."
        return f"{note}\nExtracted text snippet:\n{snippet}"

    if ftype == "spreadsheet":
        meta = file_info.get("metadata", {})
        columns = meta.get("column_names", [])
        note = f"This spreadsheet contains {meta.get('rows', 'unknown')} rows and {meta.get('columns', 'unknown')} columns."
        if columns:
            note += f" Column names include: {', '.join(columns)}."
        sample = file_info.get("content", "").strip()
        return f"{note}\nSample rows:\n{sample}"

    if ftype == "image_text":
        snippet = file_info.get("content", "").strip()[:1500]
        note = "This image appears to contain readable text extracted by OCR."
        if len(snippet) > 300:
            note += " The text may need transcription, summarization, or question answering."
        return f"{note}\nExtracted text snippet:\n{snippet}"

    if ftype == "image":
        return "This image appears to contain visual content without readable text. Describe what you want me to do next, such as identify the object, explain the scene, or answer a question about it."

    return "The file was processed, but its type could not be clearly identified."


def route(intent: str, user_input: str, file_path=None, model=None, mode=None, history=None):
    """
    Main router with chat memory support
    """

    if history is None:
        history = []

    # =========================
    # EXCEL ANALYSIS
    # =========================
    if intent == "excel_analysis":
        return analyze_excel_with_ai(
            file_path=file_path,
            model=model,
            mode=mode,
            user_input=user_input
        )

    # =========================
    # IMAGE / DOCUMENT
    # =========================
    elif intent == "document_analysis":

        file_info = process_document(file_path) if file_path else {
            "status": "error",
            "message": "No file provided for analysis."
        }
        file_context = describe_file_context(file_path, file_info)

        if mode == "Health Assistant":
            system_prompt = """
You are a practical health assistant.

You are in an ongoing conversation.

IMPORTANT:
- Do NOT repeat previous advice
- Build on previous answers
- Add NEW, more advanced or deeper guidance each time
- Detect what the document or image likely contains and explain why
- If the content shows a potential health issue, identify risks and practical next steps
- Ask one follow-up question to keep the user engaged

Respond clearly:
- What it likely is
- Why it matters
- What to do next
- What to watch for

Keep it short, empathetic, and actionable.
"""

        elif mode == "Agri Advisor":
            system_prompt = """
You are an agriculture advisor.

You are in an ongoing conversation.

IMPORTANT:
- Do NOT repeat previous answers
- Add new insights each turn
- Detect what the document or image likely contains and what it means for crops or livestock
- If the content shows a problem, explain likely cause, risks, and practical actions
- Ask one follow-up question to help the user continue the conversation

Respond clearly and practically.
"""

        else:
            system_prompt = """
You are a helpful assistant for document and image analysis.

You should:
- Identify what the file contains
- Describe the key purpose or structure of the content
- Suggest sensible next actions the user can request
- Ask one follow-up question to continue the conversation
"""

        follow_up = (
            "After describing the file, ask the user what they want next. "
            "For example, should the content be summarized, questions answered, text extracted, "
            "translated, or data extracted? If the document contains questions, mention that. "
            "If it is long, mention summarization as an option."
        )

        prompt = system_prompt + "\n\n" + file_context + "\n\n" + follow_up + "\n\n"
        prompt += build_prompt_with_history(user_input, history, "")

        image_paths = file_info.get("image_paths")
        image_bytes_list = file_info.get("image_bytes_list")

        if image_paths:
            response = generate(prompt, model=model, image_paths=image_paths)
        elif image_bytes_list:
            response = generate(prompt, model=model, image_bytes_list=image_bytes_list)
        elif file_info.get("status") == "success" and file_info.get("type") in {"image", "image_text"}:
            response = generate(prompt, model=model, image_path=file_path)
        else:
            response = generate(prompt, model=model)

        return {"status": "success", "insights": response}

    # =========================
    # GENERAL CHAT (WITH MEMORY)
    # =========================
    elif intent == "general":

        if mode == "Health Assistant":
            system_prompt = """
You are a practical health assistant.

Give concise, actionable advice.
Avoid long disclaimers.
"""

        elif mode == "Agri Advisor":
            system_prompt = """
You are an agriculture advisor.

Give short, practical advice.
"""

        else:
            system_prompt = "You are a helpful assistant."

        prompt = build_prompt_with_history(user_input, history, system_prompt)

        response = generate(prompt, model=model)

        return {"status": "success", "insights": response}

    # =========================
    # FALLBACK
    # =========================
    return {"status": "error", "message": "Unknown intent"}