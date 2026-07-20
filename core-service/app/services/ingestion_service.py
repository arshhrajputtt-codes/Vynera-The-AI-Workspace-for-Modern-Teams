import io

from docx import Document as DocxDocument
from pypdf import PdfReader

from app.core.config import settings
from app.core.exceptions import UnsupportedFileTypeError
from app.models.document import DocumentType


def detect_file_type(filename: str) -> DocumentType:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return DocumentType.PDF
    if lower.endswith(".docx"):
        return DocumentType.DOCX
    raise UnsupportedFileTypeError(filename)


def extract_text(file_bytes: bytes, file_type: DocumentType) -> str:
    if file_type == DocumentType.PDF:
        return _extract_pdf_text(file_bytes)
    if file_type == DocumentType.DOCX:
        return _extract_docx_text(file_bytes)
    raise UnsupportedFileTypeError(str(file_type))


def _extract_pdf_text(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip()


def _extract_docx_text(file_bytes: bytes) -> str:
    doc = DocxDocument(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs).strip()


def chunk_text(
    text: str,
    chunk_size_tokens: int | None = None,
    overlap_tokens: int | None = None,
) -> list[str]:
    """
    Word-count-based chunking, treating word count as a rough stand-in for
    token count (~1.3 tokens/word for English). Good enough for v1; swap in
    a real tokenizer (e.g. tiktoken) if chunk boundaries need to be exact.
    """
    chunk_size = chunk_size_tokens or settings.CHUNK_SIZE_TOKENS
    overlap = overlap_tokens or settings.CHUNK_OVERLAP_TOKENS

    words = text.split()
    if not words:
        return []

    chunks = []
    step = max(chunk_size - overlap, 1)

    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size]
        chunks.append(" ".join(chunk_words))
        if start + chunk_size >= len(words):
            break

    return chunks
