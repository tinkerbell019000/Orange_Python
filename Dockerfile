FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEADLESS=true

WORKDIR /app

# Install minimal OS packages required for Playwright's bundled Node driver
RUN apt-get update && apt-get install -y --no-install-recommends \
    libatomic1 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirement.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirement.txt && \
    playwright install --with-deps chromium

COPY . .

RUN mkdir -p reports/screenshots

CMD ["pytest", "-v", "--html=reports/test_results.html", "--self-contained-html"]
