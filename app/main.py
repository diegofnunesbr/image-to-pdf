import logging
import threading
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

from app.converter import images_to_pdf

logging.getLogger("img2pdf").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

A4_MAX_MARGIN_MM = 100
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

MAX_TOTAL_MB = 100
MAX_TOTAL_SIZE = MAX_TOTAL_MB * 1024 * 1024

stats = {"conversions": 0, "images": 0}
_stats_lock = threading.Lock()

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return stats


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/convert")
async def convert(
    files: list[UploadFile] = File(...),
    page_size: str = Form(...),
    margin: str = Form("0"),
    quality: str = Form("high"),
):

    total_size = 0
    file_streams = []

    for f in files:

        if not f.content_type or not f.content_type.startswith("image/"):
            raise HTTPException(400, "Arquivo não suportado")

        content = await f.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                400,
                f"Arquivo muito grande. Máximo {MAX_FILE_SIZE_MB} MB por imagem.",
            )

        total_size += len(content)

        if total_size > MAX_TOTAL_SIZE:
            raise HTTPException(
                400,
                f"Tamanho total excede {MAX_TOTAL_MB} MB."
            )

        f.file.seek(0)
        file_streams.append(f.file)

    margin_mm = int(margin) if margin and str(margin).isdigit() else 0

    if page_size == "A4" and margin_mm > A4_MAX_MARGIN_MM:
        raise HTTPException(
            400,
            f"Margem muito grande para A4. Use no máximo {A4_MAX_MARGIN_MM} mm.",
        )

    logger.info(f"Convertendo {len(files)} imagens")

    try:

        pdf = images_to_pdf(
            files=file_streams,
            page_size=page_size,
            margin_mm=margin_mm,
            quality=quality.strip().lower(),
        )

        with _stats_lock:
            stats["conversions"] += 1
            stats["images"] += len(files)

    except (ValueError, Exception) as e:
        msg = str(e).lower()

        if "dimension" in msg:
            raise HTTPException(
                400,
                "Imagem com resolução muito grande.",
            )

        logger.exception("Error converting images to PDF")
        raise HTTPException(500, "Erro ao converter imagens.")

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="imagens_para_pdf.pdf"'
        },
    )
