FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    librdkafka-dev gcc \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY analytics/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/    /app/shared/
COPY analytics/ /app/analytics/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "analytics.main"]
