FROM ://microsoft.com

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEADLESS=true \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN python3 -m venv /opt/venv && \
    pip install --no-cache-dir --upgrade pip

COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt && \
    playwright install --with-deps chromium

COPY . .

RUN mkdir -p reports/screenshots

CMD ["python", "-m", "pytest", "-v", "--html=reports/test_results.html", "--self-contained-html"]
