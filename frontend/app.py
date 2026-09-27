import os
import sys
from datetime import date
from pathlib import Path

import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

from backend.services.exporters import (
    format_docx,
    format_pdf,
    format_txt
)

from backend.utils.text_utils import (
    format_html_preview,
    split_terms
)


load_dotenv()


# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide"
)


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


APP_NAME = os.getenv(
    "APP_NAME",
    "LegalEase"
)


COMPANY_NAME = os.getenv(
    "COMPANY_NAME",
    "LegalEase"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        color: #777777;
        margin-bottom: 28px;
    }

    .preview {
        background: #15171a;
        color: #f4f4f4;
        padding: 24px;
        border-radius: 14px;
        max-height: 650px;
        overflow-y: auto;
        line-height: 1.7;
    }

    .preview p {
        margin-bottom: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# BACKEND FUNCTION
# =========================================================

def call_backend(payload: dict):

    response = requests.post(
        f"{BACKEND_URL}/generate",
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    data = response.json()

    return (
        data["document"],
        data.get(
            "model",
            "Gemini"
        )
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    f"""
    <div class="main-title">
        ⚖️ {APP_NAME}
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="subtitle">
        AI-Powered Legal Document Generator
    </div>
    """,
    unsafe_allow_html=True
)


st.warning(
    "LegalEase creates AI-assisted drafts, not legal advice. "
    "Review the final document with a qualified legal professional "
    "before signing or relying on it."
)


# =========================================================
# INPUT FORM
# =========================================================

with st.form("document_form"):

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # LEFT COLUMN
    # -----------------------------------------------------

    with col1:

        document_type = st.text_input(
            "Document Type",
            placeholder=(
                "Example: "
                "Non-Disclosure Agreement"
            )
        )


        parties = st.text_area(
            "Parties Involved",
            placeholder=(
                "Example: "
                "Jane Doe (Disclosing Party), "
                "TechNova Inc. (Receiving Party)"
            ),
            height=140
        )


    # -----------------------------------------------------
    # RIGHT COLUMN
    # -----------------------------------------------------

    with col2:

        effective_date = st.date_input(
            "Effective Date",
            value=date.today()
        )


        terms = st.text_area(
            "Terms & Conditions",
            placeholder=(
                "Payment within 30 days; "
                "Confidentiality must be maintained; "
                "Either party may terminate with 15 days notice"
            ),
            height=140
        )


    submitted = st.form_submit_button(
        "Generate Document",
        type="primary",
        use_container_width=True
    )


# =========================================================
# GENERATE DOCUMENT
# =========================================================

if submitted:

    if not document_type.strip():

        st.error(
            "Please enter the document type."
        )

    elif not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not terms.strip():

        st.error(
            "Please enter the terms and conditions."
        )

    else:

        payload = {

            "document_type":
                document_type.strip(),

            "parties":
                parties.strip(),

            "terms":
                terms.strip(),

            "effective_date":
                effective_date.isoformat()
        }


        with st.spinner(
            "Generating your legal document..."
        ):

            try:

                document, model = call_backend(
                    payload
                )


                st.session_state[
                    "document"
                ] = document


                st.session_state[
                    "document_type"
                ] = document_type.strip()


                st.session_state[
                    "model"
                ] = model


                st.session_state[
                    "terms"
                ] = terms.strip()


                st.success(
                    f"Document generated using {model}."
                )


            except requests.exceptions.RequestException as exc:

                detail = ""

                if exc.response is not None:

                    detail = exc.response.text


                st.error(
                    "Could not connect to the FastAPI backend.\n\n"
                    f"Backend URL: {BACKEND_URL}\n\n"
                    "Make sure the backend is running.\n\n"
                    f"{detail}"
                )


            except Exception as exc:

                st.error(
                    f"Generation failed: {exc}"
                )


# =========================================================
# DOCUMENT OUTPUT
# =========================================================

if "document" in st.session_state:

    st.divider()


    st.subheader(
        "Document Preview"
    )


    # -----------------------------------------------------
    # HTML PREVIEW
    # -----------------------------------------------------

    preview_html = format_html_preview(
        st.session_state["document"]
    )


    st.markdown(
        f"""
        <div class="preview">
            {preview_html}
        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # EDITOR
    # -----------------------------------------------------

    st.subheader(
        "Edit Document"
    )


    edited_document = st.text_area(
        "Editable document",
        value=st.session_state["document"],
        height=550,
        label_visibility="collapsed"
    )


    st.session_state[
        "document"
    ] = edited_document


    # -----------------------------------------------------
    # DOWNLOAD
    # -----------------------------------------------------

    st.subheader(
        "Download Document"
    )


    document_type = st.session_state.get(
        "document_type",
        "Legal Document"
    )


    safe_name = "".join(
        character.lower()
        if character.isalnum()
        else "_"
        for character in document_type
    ).strip("_")


    if not safe_name:

        safe_name = "legal_document"


    col1, col2, col3 = st.columns(3)


    # TXT
    with col1:

        st.download_button(
            label="Download TXT",
            data=format_txt(
                edited_document
            ),
            file_name=f"{safe_name}.txt",
            mime="text/plain",
            use_container_width=True
        )


    # DOCX
    with col2:

        st.download_button(
            label="Download DOCX",
            data=format_docx(
                edited_document,
                document_type,
                company_name=COMPANY_NAME
            ),
            file_name=f"{safe_name}.docx",
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
            use_container_width=True
        )


    # PDF
    with col3:

        st.download_button(
            label="Download PDF",
            data=format_pdf(
                edited_document,
                document_type,
                company_name=COMPANY_NAME
            ),
            file_name=f"{safe_name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


    # -----------------------------------------------------
    # INFORMATION
    # -----------------------------------------------------

    term_count = len(
        split_terms(
            st.session_state.get(
                "terms",
                ""
            )
        )
    )


    st.caption(
        f"Number of supplied terms: {term_count}"
    )