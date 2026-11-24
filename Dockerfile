FROM mcr.://microsoft.com

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEADLESS=true

WORKDIR /app

COPY requirement.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirement.txt && \
    playwright install chromium

COPY . .

RUN mkdir -p reports/screenshots

CMD ["pytest", "-v", "--html=reports/test_results.html", "--self-contained-html"]
