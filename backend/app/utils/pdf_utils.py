"""
PDF text extraction (resume upload) and PDF generation (tailored resume
download) with executive styling, clean typography, section dividers, and bullet indentation.
"""
import io
import re
from typing import Tuple

from pypdf import PdfReader
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ---------------------------------------------------------------
# Resume PDF -> text
# ---------------------------------------------------------------
def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, bool]:
    """
    Returns (extracted_text, low_confidence_flag).
    low_confidence_flag=True means the PDF looked scanned/image-based.
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    full_text = "\n".join(pages_text).strip()
    num_pages = len(reader.pages)

    if num_pages == 0:
        low_confidence = True
    else:
        low_confidence = (len(full_text) / num_pages) < 15

    return full_text, low_confidence


# ---------------------------------------------------------------
# Tailored resume text -> PDF (Usable, Attractive Template)
# ---------------------------------------------------------------
def generate_resume_pdf(content: str, candidate_name: str = "") -> bytes:
    """
    Renders the FINAL, human-approved tailored resume text into a clean,
    usable, attractive downloadable PDF template without placeholder headers.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()

    # Executive Modern Color Palette
    PRIMARY_COLOR = colors.HexColor("#0F172A")    # Deep Slate
    ACCENT_COLOR = colors.HexColor("#1E3A8A")     # Royal Blue
    TEXT_MAIN = colors.HexColor("#1E293B")        # Dark Charcoal
    BORDER_COLOR = colors.HexColor("#94A3B8")     # Slate Border

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=PRIMARY_COLOR,
        alignment=TA_LEFT,
        spaceAfter=4,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=ACCENT_COLOR,
        spaceBefore=10,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=TEXT_MAIN,
        alignment=TA_LEFT,
        spaceAfter=3,
    )

    bullet_style = ParagraphStyle(
        "BulletBody",
        parent=body_style,
        leftIndent=14,
        bulletIndent=4,
        spaceAfter=2,
    )

    story = []

    lines = [l.strip() for l in content.split("\n") if l.strip()]

    # If first line is a main header (e.g. # Name), extract it as Title
    first_line_is_title = False
    if lines and lines[0].startswith("#"):
        name_text = lines[0].lstrip("#").strip()
        story.append(Paragraph(name_text.upper(), title_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_COLOR, spaceBefore=2, spaceAfter=8))
        first_line_is_title = True
    elif candidate_name and "@" not in candidate_name:
        story.append(Paragraph(candidate_name.upper(), title_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_COLOR, spaceBefore=2, spaceAfter=8))

    raw_lines = content.split("\n")
    if first_line_is_title and len(raw_lines) > 0:
        raw_lines = raw_lines[1:]

    # Render body lines
    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 4))
            continue

        # Section Headings (# or ## or ###)
        if line.startswith("#"):
            clean_heading = line.lstrip("#").strip().upper()
            story.append(Paragraph(clean_heading, heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=1, spaceAfter=4))
        # Bullet Points (- or * or •)
        elif line.startswith(("-", "*", "•")):
            bullet_text = line.lstrip("-*•").strip()
            safe = bullet_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            safe = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe)
            story.append(Paragraph(f"• {safe}", bullet_style))
        else:
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            safe = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe)
            story.append(Paragraph(safe, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
