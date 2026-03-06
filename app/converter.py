from io import BytesIO

import img2pdf
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

QUALITY_LOW = ("low", "small")
QUALITY_BALANCED = ("balanced",)

JPEG_QUALITY_LOW = 50
JPEG_QUALITY_BALANCED = 75

DPI_LOW = 100
DPI_BALANCED = 150

MAX_RESOLUTION = 12000

PT_PER_INCH = 72
MM_PER_INCH = 25.4

A4_MM = (210, 297)


def _to_pdf_reportlab(files, page_size, margin_mm, quality):

    buf = BytesIO()
    c = canvas.Canvas(buf)

    if quality in QUALITY_BALANCED:
        jpeg_quality = JPEG_QUALITY_BALANCED
        dpi = DPI_BALANCED
    else:
        jpeg_quality = JPEG_QUALITY_LOW
        dpi = DPI_LOW

    for file_obj in files:

        img = Image.open(file_obj)

        if img.width > MAX_RESOLUTION or img.height > MAX_RESOLUTION:
            raise ValueError("dimension too large")

        img = img.convert("RGB")

        jpg = BytesIO()

        img.save(
            jpg,
            format="JPEG",
            quality=jpeg_quality,
            optimize=True,
            dpi=(dpi, dpi),
        )

        jpg.seek(0)

        w_px, h_px = img.size

        w_pt = w_px * PT_PER_INCH / dpi
        h_pt = h_px * PT_PER_INCH / dpi

        reader = ImageReader(jpg)

        if page_size == "A4":

            pw, ph = A4

            m = margin_mm * PT_PER_INCH / MM_PER_INCH

            scale = min((pw - 2 * m) / w_pt, (ph - 2 * m) / h_pt)

            dw, dh = w_pt * scale, h_pt * scale

            x, y = (pw - dw) / 2, (ph - dh) / 2

            c.setPageSize(A4)

            c.drawImage(reader, x, y, dw, dh)

        else:

            c.setPageSize((w_pt, h_pt))
            c.drawImage(reader, 0, 0, w_pt, h_pt)

        c.showPage()

    c.save()

    buf.seek(0)

    return buf.read()


def _to_pdf_img2pdf(files, page_size, margin_mm):

    margin_pt = img2pdf.mm_to_pt(margin_mm)

    layout = (
        img2pdf.get_layout_fun(
            pagesize=(
                img2pdf.mm_to_pt(A4_MM[0]),
                img2pdf.mm_to_pt(A4_MM[1]),
            ),
            border=(margin_pt, margin_pt),
        )
        if page_size == "A4"
        else img2pdf.default_layout_fun
    )

    return img2pdf.convert(
        *files,
        layout_fun=layout,
        rotation=img2pdf.Rotation.ifvalid,
    )


def images_to_pdf(files, page_size, margin_mm, quality):

    if quality in QUALITY_LOW or quality in QUALITY_BALANCED:
        return _to_pdf_reportlab(files, page_size, margin_mm, quality)

    return _to_pdf_img2pdf(files, page_size, margin_mm)
