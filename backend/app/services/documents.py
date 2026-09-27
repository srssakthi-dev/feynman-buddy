"""Readable PDF -> page-linked passages. No marking statements or topic rules."""
import io
import re
from pypdf import PdfReader

MAX_BYTES = 10 * 1024 * 1024
MAX_PAGES = 20


def extract_notes(data: bytes, filename: str) -> dict:
    if len(data) > MAX_BYTES:
        raise ValueError("Choose a PDF smaller than 10 MB.")
    if not data.startswith(b"%PDF-"):
        raise ValueError("Choose a PDF file with selectable text.")
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise ValueError("This PDF is encrypted. Upload an unencrypted copy.")
        if not 1 <= len(reader.pages) <= MAX_PAGES:
            raise ValueError("Use a short set of notes, between 1 and 20 pages.")
        chunks, warnings = [], []
        total_characters = 0
        for page_number, page in enumerate(reader.pages, 1):
            # Layout mode favours visual reading order, including PDFs with footer-first streams.
            text = page.extract_text(extraction_mode="layout") or ""
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(line for line in lines if not line.isdigit())
            total_characters += len(text)
            if len(text) > 25000 or total_characters > 150000:
                raise ValueError("These notes contain too much text. Upload a shorter extract.")
            if len(re.sub(r"\s", "", text)) < 25:
                warnings.append(f"Page {page_number} has little readable text. Image-only content is not included yet.")
                continue
            words = text.split()
            # Small overlapping windows keep local context without requiring specific headings.
            for start in range(0, len(words), 150):
                window = words[start:start + 180]
                if not window:
                    continue
                chunks.append({"id": f"P{page_number}C{start // 150 + 1}",
                               "page": page_number, "text": " ".join(window)})
                if start + 180 >= len(words):
                    break
        if not chunks:
            raise ValueError("No usable text was found. Scanned/image-only PDFs need OCR; use selectable-text notes for now.")
        if len(chunks) > 200:
            raise ValueError("Please upload a shorter extract of your notes.")
        return {"filename": filename.replace("\\", "/").split("/")[-1][:180] or "notes.pdf",
                "page_count": len(reader.pages), "chunks": chunks, "warnings": warnings}
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("This PDF could not be read. Try exporting a fresh PDF with selectable text.") from exc
