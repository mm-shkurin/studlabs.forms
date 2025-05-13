FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip list | grep uvicorn

CMD ["uvicorn", "LabForm.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--reload"]