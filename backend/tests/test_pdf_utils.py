import io
from reportlab.pdfgen import canvas
from app.utils.pdf_utils import extract_text_from_pdf, generate_resume_pdf


def _make_sample_pdf_bytes(text: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(72, 750, text)
    c.save()
    return buf.getvalue()


def test_extract_text_from_pdf_reads_real_text():
    pdf_bytes = _make_sample_pdf_bytes("Jane Doe - Software Engineer")
    text, low_confidence = extract_text_from_pdf(pdf_bytes)
    assert "Jane Doe" in text
    assert low_confidence is False


def test_extract_text_from_pdf_flags_empty_pdf_as_low_confidence():
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.showPage()
    c.save()
    text, low_confidence = extract_text_from_pdf(buf.getvalue())
    assert low_confidence is True


def test_generate_resume_pdf_produces_nonempty_pdf_bytes():
    content = "## Summary\nExperienced engineer.\n## Skills\nPython, FastAPI"
    pdf_bytes = generate_resume_pdf(content, candidate_name="Jane Doe")
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 500
