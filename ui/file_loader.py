from io import BytesIO

from docx import Document
from pypdf import PdfReader


def extract_text_from_upload(uploaded_file) -> str:
    """Streamlit file_uploader ile gelen dosyadan metin çıkarır."""

    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if file_name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")

    if file_name.endswith(".docx"):
        document = Document(BytesIO(file_bytes))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        return "\n".join(paragraphs).strip()

    if file_name.endswith(".pdf"):
        reader = PdfReader(BytesIO(file_bytes))
        pages_text = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

        return "\n".join(pages_text).strip()

    raise ValueError("Desteklenmeyen dosya türü. Lütfen .txt, .docx veya .pdf yükleyin.")