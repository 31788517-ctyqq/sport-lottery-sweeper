FROM python:3.11-slim

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_RETRIES=3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt
RUN pip install --no-cache-dir \
    slowapi \
    selenium \
    email-validator \
    pyjwt \
    fake-useragent \
    aiosqlite \
    asyncpg \
    psycopg2-binary \
    python-multipart \
    psutil \
    google-genai \
    flask \
    flask-sqlalchemy \
    zhipuai

COPY . .

EXPOSE 8000

CMD ["python", "backend/main.py"]
