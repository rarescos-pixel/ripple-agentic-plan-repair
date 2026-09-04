FROM python:3.13-slim
WORKDIR /app
COPY runtime.part*.b64 /tmp/runtime_parts/
RUN cat /tmp/runtime_parts/runtime.part*.b64 | base64 -d > /tmp/runtime.tar.gz \
    && tar -xzf /tmp/runtime.tar.gz -C /app \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && rm -rf /tmp/runtime_parts /tmp/runtime.tar.gz
ENV PYTHONPATH=/app/src
EXPOSE 8000
CMD ["python", "-m", "ripple.mcp_server"]
