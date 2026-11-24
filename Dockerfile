FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEADLESS=true

WORKDIR /app

COPY requirement.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirement.txt && \
    playwright install --with-deps chromium

COPY . .

RUN mkdir -p reports/screenshots

CMD ["pytest", "-v", "--html=reports/test_results.html", "--self-contained-html"]
