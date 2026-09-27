import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


load_dotenv(Path(__file__).parents[2] / "frontend" / ".env")


def _client() -> tuple[genai.Client, str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    return genai.Client(api_key=api_key), os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _generate(prompt: str) -> str:
    client, model = _client()
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text or "No response was returned."


def analyze_document(document_text: str) -> dict[str, str]:
    result = _generate(
        "Analyze this legal document. Return a concise summary, key obligations, "
        "important dates, risks, and suggested questions.\n\n"
        f"Document:\n{document_text}"
    )
    return {"result": result}


def ask_document_question(document_text: str, question: str) -> str:
    return _generate(
        "Answer the question using only the legal document below. State when the "
        "document does not provide enough information.\n\n"
        f"Document:\n{document_text}\n\nQuestion:\n{question}"
    )


def generate_document(
    document_type: str,
    parties: str,
    terms: str,
    effective_date: str,
) -> str:
    return _generate(
        "Draft a clear legal document from the following requirements. Use plain "
        "professional language, include appropriate headings, and do not provide "
        "legal advice outside the draft.\n\n"
        f"Document type: {document_type}\n"
        f"Parties: {parties}\n"
        f"Effective date: {effective_date}\n"
        f"Terms and conditions: {terms}"
    )
