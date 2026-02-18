# Image to PDF

Aplicação web para converter imagens em PDF, com suporte a:

- múltiplas imagens
- reordenação
- A4 / Original
- margens
- qualidade máxima (sem perda)
- arquivo menor
- limite de 10 MB por imagem

## Estrutura do repositório

```text
image-to-pdf/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── converter.py
│   └── templates/
│       └── index.html
├── Dockerfile
├── requirements.txt
└── README.md
```

Acesse: http://localhost:8000

## Como rodar localmente

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tecnologias

- Python
- FastAPI
- Pillow
- img2pdf
- HTML / CSS / JS
- Docker

## Observações

- Nenhum dado é armazenado
- Processamento em memória

## Como rodar com Docker

```bash
docker build -t image-to-pdf .
docker run -p 8000:8000 image-to-pdf
```
