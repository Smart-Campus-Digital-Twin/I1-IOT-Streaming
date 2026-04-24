FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    librdkafka-dev gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY processor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/    /app/shared/
COPY processor/ /app/processor/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "processor.main"]
