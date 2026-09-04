FROM python:3.13-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app/src
EXPOSE 8000
CMD ["python", "-m", "ripple.mcp_server"]
