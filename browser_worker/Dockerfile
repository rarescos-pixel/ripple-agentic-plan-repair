FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    BROWSER_PROFILE_DIR=/data/chromium-profile \
    AWS_VERIFY_STATUS_FILE=/data/chromium-profile/aws_verify.json

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install --with-deps chromium \
    && chmod -R a+rx /ms-playwright

COPY app.py ./
COPY verify_startup.py ./

RUN addgroup --system broker \
    && adduser --system --ingroup broker broker \
    && mkdir -p /data/chromium-profile \
    && chown -R broker:broker /data

USER broker

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + __import__('os').getenv('PORT','8000') + '/healthz', timeout=2).read()"

CMD ["sh", "-c", "python verify_startup.py; exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --no-access-log --log-level warning"]
