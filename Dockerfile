FROM python:latest
LABEL authors="systemhub144"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN useradd -m -u 1000 fastapi-user && chown -R fastapi-user:fastapi-user /app

USER fastapi-user

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]