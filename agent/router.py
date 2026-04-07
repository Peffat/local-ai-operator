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

        # IMAGE → MULTIMODAL
        if file_path and file_path.lower().endswith((".png", ".jpg", ".jpeg")):

            if mode == "Health Assistant":
                system_prompt = """
You are a practical health assistant.

You are in an ongoing conversation.

IMPORTANT:
- Do NOT repeat previous advice
- Build on previous answers
- Add NEW, more advanced or deeper guidance each time
- If the user clarifies (e.g., "it's a dog bite"), adjust your advice accordingly

Respond concisely:
- What it likely is (if needed)
- What to do next (NEW advice)
- Important risks (only if not already mentioned)

Keep it short and practical.
"""

            elif mode == "Agri Advisor":
                system_prompt = """
You are an agriculture advisor.

You are in an ongoing conversation.

IMPORTANT:
- Do NOT repeat previous answers
- Add new insights each turn
- Adjust advice based on new user input

Keep advice practical and concise.
"""

            else:
                system_prompt = "Describe and analyze the image clearly."

            prompt = build_prompt_with_history(user_input, history, system_prompt)

            response = generate(
                prompt,
                model=model,
                image_path=file_path
            )

            return {"status": "success", "insights": response}

        # NON-IMAGE DOC
        return process_document(file_path)

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