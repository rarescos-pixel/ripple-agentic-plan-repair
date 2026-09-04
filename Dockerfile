FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    RIPPLE_HOST=0.0.0.0 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN addgroup --system ripple && adduser --system --ingroup ripple ripple

COPY requirements.txt README.md LICENSE ./
COPY src ./src
COPY fixtures ./fixtures
COPY docs ./docs
COPY scripts ./scripts

RUN pip install --no-cache-dir -r requirements.txt

USER ripple
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + __import__('os').getenv('PORT','8000') + '/readyz', timeout=2).read()"

CMD ["sh", "-c", "uvicorn ripple.asgi:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
