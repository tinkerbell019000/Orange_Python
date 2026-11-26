FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEADLESS=true \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libatomic1 ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv && \
    pip install --no-cache-dir --upgrade pip

COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt && \
    playwright install --with-deps --only-shell chromium

COPY . .

RUN mkdir -p reports/screenshots

CMD ["pytest", "-v"]
