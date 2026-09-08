from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt", ".csv"}


@dataclass(frozen=True)
class ParsedSection:
    text: str
    page: int | None = None
    section: str | None = None
    content_type: str = "text/plain"


def _parse_markdown(text: str) -> list[ParsedSection]:
    sections: list[ParsedSection] = []
    current_section: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        body = "\n".join(buffer).strip()
        if not body:
            buffer.clear()
            return
        section_text = f"{current_section}\n{body}" if current_section else body
        sections.append(
            ParsedSection(
                text=section_text,
                section=current_section,
                content_type="text/markdown",
            )
        )
        buffer.clear()

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            marker_count = len(stripped) - len(stripped.lstrip("#"))
            is_heading = (
                1 <= marker_count <= 6
                and len(stripped) > marker_count
                and stripped[marker_count] == " "
            )
            if is_heading:
                flush()
                current_section = stripped[marker_count:].strip()
                continue
        buffer.append(line)

    flush()
    return sections


def parse_file(path: Path) -> list[ParsedSection]:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}")

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        sections = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                sections.append(
                    ParsedSection(
                        text=text,
                        page=page_number,
                        section=f"Page {page_number}",
                        content_type="application/pdf",
                    )
                )
        return sections

    text = path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".md":
        return _parse_markdown(text)

    content_type = "text/csv" if suffix == ".csv" else "text/plain"
    return [ParsedSection(text=text, content_type=content_type)]
