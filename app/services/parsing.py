import io
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.core.config import settings


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )


def split_text(text: str) -> list[str]:
    return _splitter().split_text(_clean(text))


def extract_text(content: bytes, mime_type: str) -> str:
    if mime_type == "application/pdf":
        reader = PdfReader(io.BytesIO(content))
        return _clean("\n\n".join(page.extract_text() or "" for page in reader.pages))
    return _clean(content.decode("utf-8", errors="replace"))


def extract_text_by_page(content: bytes) -> list[tuple[int, str]]:
    """Returns [(1-indexed page_num, page_text), ...] for PDFs."""
    reader = PdfReader(io.BytesIO(content))
    return [(i + 1, _clean(page.extract_text() or "")) for i, page in enumerate(reader.pages)]
