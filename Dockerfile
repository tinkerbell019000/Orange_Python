FROM ://microsoft.com

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEADLESS=true \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Create an isolated virtual environment (avoids PEP 668 & PATH issues)
RUN python3 -m venv /opt/venv && \
    pip install --no-cache-dir --upgrade pip

# Install Python packages and matching Chromium browser + OS libraries
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt && \
    playwright install --with-deps chromium

# Copy project source code
COPY . .

RUN mkdir -p reports/screenshots

CMD ["python", "-m", "pytest", "-v", "--html=reports/test_results.html", "--self-contained-html"]
