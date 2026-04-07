def detect_intent(user_input: str) -> dict:
    text = user_input.lower()

    if any(w in text for w in ["excel", "csv", "data", "analyze"]):
        return {"intent": "excel_analysis"}

    if any(w in text for w in ["pdf", "document", "file"]):
        return {"intent": "document_analysis"}

    # default
    return {"intent": "general"}