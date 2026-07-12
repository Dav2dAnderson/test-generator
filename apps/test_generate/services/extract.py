import os
from pypdf import PdfReader
from docx import Document

class UnsupportedFileTypeError(Exception):
    pass

def _extract_from_pdf(file_field) -> str:
    reader = PdfReader(file_field)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def _extract_from_docx(file_field) -> str:
    doc = Document(file_field)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


def _extract_from_txt(file_field) -> str:
    content = file_field.read()
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    return content.strip()

def extract_text_from_file(file_field) -> str:
    """
    Django FileField/UploadedFile obyektidan matn ajratib oladi.
    Qo'llab-quvvatlanadigan formatlar: .pdf, .docx, .txt
    """

    filename = file_field.name
    ext = os.path.splitext(filename)[1].lower()

    if ext == '.pdf':
        return _extract_from_pdf(file_field)
    elif ext == '.docx':
        return _extract_from_docx(file_field)
    elif ext == '.txt':
        return _extract_from_txt(file_field)
    else:
        raise UnsupportedFileTypeError(
            f"'{ext}' formati qo'llab-quvvatlanmaydi. Faqat .pdf, .docx, .txt fayllarini yuklang."
        )