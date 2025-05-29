FROM python:3.11-bookworm

RUN apt-get update && apt-get install -y \
    git build-essential curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    --trusted-host pypi.org --trusted-host files.pythonhosted.org

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]