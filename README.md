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

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `MAX_FILE_SIZE_MB` | 10 | Tamanho máximo por imagem (MB) |
| `MAX_TOTAL_MB` | 100 | Tamanho total máximo (MB) |
| `A4_MAX_MARGIN_MM` | 100 | Margem máxima para A4 (mm) |

## Como rodar com Docker

```bash
docker build -t image-to-pdf .
docker run -d -p 8000:8000 \
  --restart unless-stopped \
  --name image-to-pdf \
  image-to-pdf
```

## Consultar os logs

```bash
docker logs -f image-to-pdf
```
