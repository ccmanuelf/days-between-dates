# The app in one container: the API and the page, with the SQLite file in /data (a volume in compose.yaml).
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DBD_DB_PATH=/data/app.db

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Run as a user without root rights; it owns /data, where the database is created at start.
RUN useradd --create-home --uid 10001 app && mkdir /data && chown app /data
USER app

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
