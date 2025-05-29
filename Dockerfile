FROM python:3.11-bookworm

# Устанавливаем python-dotenv и базовые системные зависимости
RUN pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org && \
    pip install python-dotenv --trusted-host pypi.org --trusted-host files.pythonhosted.org

RUN apt-get update && apt-get install -y \
    git build-essential curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Указываем рабочую директорию
WORKDIR /app

# ✅ Копируем только requirements.txt, чтобы кэшировался pip install
COPY requirements.txt .

# ✅ Устанавливаем зависимости — будет использоваться слой кэша, если файл не менялся
RUN pip install --no-cache-dir -r requirements.txt \
    --trusted-host pypi.org --trusted-host files.pythonhosted.org

# ✅ Теперь копируем остальной код проекта
COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем FastAPI через Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
