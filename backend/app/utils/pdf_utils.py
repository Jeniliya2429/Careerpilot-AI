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
    executive, ATS-compliant downloadable PDF template with candidate header,
    contact info bar, clear section dividers, and bold bullet points.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
    )

    styles = getSampleStyleSheet()

    # Executive Modern Color Palette
    PRIMARY_COLOR = colors.HexColor("#0F172A")    # Deep Slate
    ACCENT_COLOR = colors.HexColor("#1E3A8A")     # Royal Navy
    TEXT_MAIN = colors.HexColor("#1E293B")        # Dark Charcoal
    TEXT_MUTED = colors.HexColor("#475569")       # Slate Muted
    BORDER_COLOR = colors.HexColor("#CBD5E1")     # Light Slate Divider

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=PRIMARY_COLOR,
        alignment=TA_LEFT,
        spaceAfter=2,
    )

    contact_style = ParagraphStyle(
        "ContactInfo",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT_MUTED,
        alignment=TA_LEFT,
        spaceAfter=4,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=ACCENT_COLOR,
        spaceBefore=8,
        spaceAfter=3,
    )

    subheading_style = ParagraphStyle(
        "JobSubheading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=TEXT_MAIN,
        spaceBefore=4,
        spaceAfter=2,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=TEXT_MAIN,
        alignment=TA_LEFT,
        spaceAfter=2,
    )

    bullet_style = ParagraphStyle(
        "BulletBody",
        parent=body_style,
        leftIndent=12,
        bulletIndent=3,
        spaceAfter=2,
    )

    story = []
    raw_lines = [l.rstrip() for l in content.split("\n")]
    
    # Check for candidate name on line 1 or fallback
    header_handled = False
    idx = 0
    while idx < len(raw_lines) and not raw_lines[idx].strip():
        idx += 1

    if idx < len(raw_lines) and raw_lines[idx].strip().startswith("# "):
        # Line is '# Candidate Name'
        name_text = raw_lines[idx].strip()[2:].strip()
        story.append(Paragraph(name_text.upper(), title_style))
        idx += 1
        
        # Check next line for contact info
        while idx < len(raw_lines) and not raw_lines[idx].strip():
            idx += 1
            
        if idx < len(raw_lines) and not raw_lines[idx].strip().startswith("#"):
            contact_text = raw_lines[idx].strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(contact_text, contact_style))
            idx += 1
            
        story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceBefore=2, spaceAfter=6))
        header_handled = True
    elif candidate_name:
        clean_name = candidate_name.split("@")[0].replace(".", " ").replace("_", " ").title()
        story.append(Paragraph(clean_name.upper(), title_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceBefore=2, spaceAfter=6))
        header_handled = True

    # Render remaining lines
    while idx < len(raw_lines):
        line = raw_lines[idx].strip()
        idx += 1
        if not line:
            story.append(Spacer(1, 3))
            continue

        # Level 3 Heading (Job / Project Subheading: ### Title | Company | Dates)
        if line.startswith("### "):
            clean_sub = line[4:].strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            clean_sub = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_sub)
            story.append(Paragraph(clean_sub, subheading_style))
        # Level 2 Heading (Section: ## Experience / ## Education)
        elif line.startswith("## ") or (line.startswith("# ") and header_handled):
            clean_heading = line.lstrip("#").strip().upper()
            story.append(Paragraph(clean_heading, heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=1, spaceAfter=3))
        # Bullet Points (- or * or •)
        elif line.startswith(("- ", "* ", "• ", "-*", "*•")):
            bullet_text = re.sub(r'^[-*•\s]+', '', line).strip()
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
