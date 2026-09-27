from html import escape


def split_terms(terms: str) -> list[str]:
    return [term.strip() for term in terms.replace("\n", ";").split(";") if term.strip()]


def format_html_preview(document: str) -> str:
    paragraphs = [paragraph.strip() for paragraph in document.splitlines() if paragraph.strip()]
    return "".join(f"<p>{escape(paragraph)}</p>" for paragraph in paragraphs)
