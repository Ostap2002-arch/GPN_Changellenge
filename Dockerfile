FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы с зависимостями
COPY pyproject.toml poetry.lock* ./
# Ensure package sources are available so Poetry can install the project
# (Poetry needs the package files present when installing the current project)
COPY device_data_service ./device_data_service

# Устанавливаем Poetry и зависимости (исключая dev)
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without dev --no-interaction --no-ansi

# Expose port
EXPOSE 8000

# Копируем код
COPY . .

CMD ["python", "-m", "uvicorn", "device_data_service.main:app", "--host", "0.0.0.0", "--port", "8000"]