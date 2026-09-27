from io import BytesIO

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def format_txt(document: str) -> str:
    return document


def format_docx(document: str, document_type: str, company_name: str = "") -> bytes:
    output = BytesIO()
    doc = Document()
    doc.add_heading(document_type, level=1)
    if company_name:
        doc.add_paragraph(company_name)
    for paragraph in document.splitlines():
        if paragraph.strip():
            doc.add_paragraph(paragraph)
    doc.save(output)
    return output.getvalue()


def format_pdf(document: str, document_type: str, company_name: str = "") -> bytes:
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=letter)
    width, height = letter
    y = height - 54
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(54, y, document_type[:90])
    y -= 24
    if company_name:
        pdf.setFont("Helvetica", 10)
        pdf.drawString(54, y, company_name[:110])
        y -= 22
    pdf.setFont("Helvetica", 10)
    for paragraph in document.splitlines():
        words = paragraph.split()
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if pdf.stringWidth(candidate, "Helvetica", 10) > width - 108:
                pdf.drawString(54, y, line)
                y -= 14
                line = word
            else:
                line = candidate
        if line:
            pdf.drawString(54, y, line)
            y -= 14
        if y < 54:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = height - 54
    pdf.save()
    return output.getvalue()
