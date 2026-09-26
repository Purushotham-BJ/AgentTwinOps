FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Explicitly set python path so imports work correctly
ENV PYTHONPATH=/app

CMD ["uvicorn", "app.core.factory:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
