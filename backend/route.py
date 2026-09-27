from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from pathlib import Path
import uuid

from backend.ai_core.gemini_generator import analyze_document, generate_document
from backend.document_utils.formatters import extract_text_from_pdf


router = APIRouter(
    prefix="/api",
    tags=["LegalEase"]
)


# Temporary storage for uploaded documents
documents = {}


class DocumentRequest(BaseModel):
    document_type: str
    parties: str
    terms: str
    effective_date: str


@router.post("/generate")
def generate_legal_document(request: DocumentRequest):
    if not all((request.document_type.strip(), request.parties.strip(), request.terms.strip())):
        raise HTTPException(
            status_code=400,
            detail="Document type, parties, and terms are required.",
        )

    document = generate_document(
        request.document_type,
        request.parties,
        request.terms,
        request.effective_date,
    )

    return {
        "document": document,
        "model": "Gemini",
    }


@router.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF and analyze it using Gemini AI.
    """

    # Check file type
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    try:
        # Read uploaded PDF
        pdf_bytes = await file.read()

        if not pdf_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        # Create unique document ID
        document_id = str(uuid.uuid4())

        # Save uploaded document
        data_folder = Path("data")
        data_folder.mkdir(exist_ok=True)

        pdf_path = data_folder / f"{document_id}.pdf"

        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_bytes)

        # Extract text from PDF
        document_text = extract_text_from_pdf(pdf_path)

        if not document_text.strip():
            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text found in the PDF. "
                    "Please upload a text-based PDF."
                )
            )

        # Send document to Gemini
        result = analyze_document(document_text)

        # Store document information
        documents[document_id] = {
            "filename": file.filename,
            "text": document_text,
            "analysis": result
        }

        return {
            "success": True,
            "document_id": document_id,
            "filename": file.filename,
            "analysis": result
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document analysis failed: {str(error)}"
        )


@router.get("/document/{document_id}")
def get_document(document_id: str):
    """
    Get previously analyzed document.
    """

    document = documents.get(document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "success": True,
        "document_id": document_id,
        "filename": document["filename"],
        "analysis": document["analysis"]
    }


@router.post("/chat")
async def ask_question(
    document_id: str,
    question: str
):
    """
    Ask a question about an uploaded document.
    """

    document = documents.get(document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    if not question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        from backend.ai_core.gemini_generator import ask_document_question

        answer = ask_document_question(
            document["text"],
            question
        )

        return {
            "success": True,
            "question": question,
            "answer": answer
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {str(error)}"
        )