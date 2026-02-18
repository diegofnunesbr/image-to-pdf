from io import BytesIO

import img2pdf
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

QUALITY_LOW = ("low", "small")
JPEG_QUALITY = 50
DPI_LOW = 100
PT_PER_INCH = 72
MM_PER_INCH = 25.4
A4_MM = (210, 297)


def _to_pdf_reportlab(files: list[bytes], page_size: str, margin_mm: int) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf)

    for data in files:
        img = Image.open(BytesIO(data)).convert("RGB")
        jpg = BytesIO()
        img.save(jpg, format="JPEG", quality=JPEG_QUALITY, optimize=True, dpi=(DPI_LOW, DPI_LOW))
        jpg.seek(0)

        w_px, h_px = img.size
        w_pt = w_px * PT_PER_INCH / DPI_LOW
        h_pt = h_px * PT_PER_INCH / DPI_LOW
        reader = ImageReader(jpg)

        if page_size == "A4":
            pw, ph = A4
            m = margin_mm * PT_PER_INCH / MM_PER_INCH
            scale = min((pw - 2 * m) / w_pt, (ph - 2 * m) / h_pt)
            dw, dh = w_pt * scale, h_pt * scale
            x, y = (pw - dw) / 2, (ph - dh) / 2
            c.setPageSize(A4)
            c.drawImage(reader, x, y, dw, dh, preserveAspectRatio=True, mask="auto")
        else:
            c.setPageSize((w_pt, h_pt))
            c.drawImage(reader, 0, 0, w_pt, h_pt, preserveAspectRatio=True, mask="auto")

        c.showPage()

    c.save()
    buf.seek(0)
    return buf.read()


def _to_pdf_img2pdf(files: list[bytes], page_size: str, margin_mm: int) -> bytes:
    margin_pt = img2pdf.mm_to_pt(margin_mm)
    layout = (
        img2pdf.get_layout_fun(
            pagesize=(img2pdf.mm_to_pt(A4_MM[0]), img2pdf.mm_to_pt(A4_MM[1])),
            border=(margin_pt, margin_pt),
        )
        if page_size == "A4"
        else img2pdf.default_layout_fun
    )
    return img2pdf.convert(*files, layout_fun=layout, rotation=img2pdf.Rotation.ifvalid)


def images_to_pdf(files: list[bytes], page_size: str, margin_mm: int, quality: str) -> bytes:
    if quality in QUALITY_LOW:
        return _to_pdf_reportlab(files, page_size, margin_mm)
    return _to_pdf_img2pdf(files, page_size, margin_mm)
