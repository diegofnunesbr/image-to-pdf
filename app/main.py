import logging

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

from app.converter import images_to_pdf

logging.getLogger("img2pdf").setLevel(logging.WARNING)

app = FastAPI()
A4_MAX_MARGIN_MM = 100
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024
templates = Jinja2Templates(directory="app/templates")


@app.get("/health")
async def health():
    return {"status": "ok"}


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
    file_bytes = []
    for f in files:
        content = await f.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande. Máximo {MAX_FILE_SIZE_MB} MB por imagem.",
            )
        file_bytes.append(content)

    margin_mm = int(margin) if margin and str(margin).isdigit() else 0

    if page_size == "A4" and margin_mm > A4_MAX_MARGIN_MM:
        raise HTTPException(
            status_code=400,
            detail=f"Margem muito grande para A4. Use no máximo {A4_MAX_MARGIN_MM} mm.",
        )

    try:
        pdf = images_to_pdf(
            files=file_bytes,
            page_size=page_size,
            margin_mm=margin_mm,
            quality=quality.strip().lower(),
        )
    except (ValueError, Exception) as e:
        msg = str(e).lower()
        if "border" in msg or "margin" in msg or "dimension" in msg or "negative" in msg:
            raise HTTPException(
                status_code=400,
                detail=f"Margem muito grande para a página A4. Use no máximo {A4_MAX_MARGIN_MM} mm.",
            )
        raise HTTPException(status_code=500, detail="Erro ao converter imagens.")

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="imagens_para_pdf.pdf"'},
    )
