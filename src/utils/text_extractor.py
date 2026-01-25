"""Text extraction utility for PDF and DOCX files."""
from io import BytesIO
from typing import Optional
from src.utils.logger import get_logger

class TextExtractor:
    """Utility for extracting text from various file formats."""
    
    _logger = get_logger(__name__)

    @classmethod
    async def extract_text(cls, content: bytes, file_type: str) -> str:
        """Extract text from bytes based on file type."""
        if file_type == 'pdf':
            return await cls._extract_from_pdf(content)
        elif file_type == 'docx':
            return await cls._extract_from_docx(content)
        return ""

    @classmethod
    async def _extract_from_pdf(cls, content: bytes) -> str:
        """Extract text from PDF."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(BytesIO(content))
            return f"<p><strong>PDF Document</strong></p><p>{len(reader.pages)} page(s)</p>"
        except Exception as e:
            cls._logger.error(f"PDF extraction failed: {e}")
            return f"[PDF error: {str(e)}]"

    @classmethod
    async def _extract_from_docx(cls, content: bytes) -> str:
        """Extract text from DOCX."""
        try:
            from docx import Document
            doc = Document(BytesIO(content))
            return cls._convert_docx_to_html(doc)
        except Exception as e:
            cls._logger.error(f"DOCX extraction failed: {e}")
            return f"[DOCX error: {str(e)}]"

    @classmethod
    def _convert_docx_to_html(cls, doc) -> str:
        """Convert DOCX paragraphs to HTML string."""
        html_parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                html_parts.append(f"<p>{para.text}</p>")
        return "".join(html_parts)

