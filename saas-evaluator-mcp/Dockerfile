FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
ENV ANTHROPIC_API_KEY=""
ENV EVAL_DATA_DIR="/data"
VOLUME ["/data"]
EXPOSE 8000
CMD ["python", "server.py"]
