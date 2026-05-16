# Device Data Service

![Architecture](image)

Сбор показаний устройств, асинхронный анализ и REST API.

## В проекте

- FastAPI + Swagger UI
- PostgreSQL + SQLAlchemy
- Celery + Redis
- Пагинация для `/devices/{device_id}/readings`
- Результаты нагрузочного тестирования: `Locust.html`

## Быстрый запуск

```bash
git clone https://github.com/Ostap2002-arch/GPN_Changellenge.git
cd GPN
python -m venv venv
venv\Scripts\activate
pip install poetry
poetry install
python -m uvicorn device_data_service.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker-compose up -d
```

## API Endpoints

### Здоровье приложения
- `GET /health` - Проверка статуса приложения

### Устройства
- `POST /devices` - Создать новое устройство
- `GET /devices` - Получить список всех устройств
- `GET /devices/{device_id}` - Получить информацию об устройстве
- `DELETE /devices/{device_id}` - Удалить устройство

### Показания устройства
- `POST /devices/{device_id}/readings` - Добавить показание
- `GET /devices/{device_id}/readings` - Получить показания
  - Параметры запроса:
    - `start_time` (optional): ISO 8601 datetime
    - `end_time` (optional): ISO 8601 datetime

### Анализ данных
- `GET /analysis/device/{device_id}` - Анализ всех показаний
- `GET /analysis/device/{device_id}/last-24h` - Анализ за последние 24 часа
- `GET /analysis/device/{device_id}/last-7d` - Анализ за последние 7 дней

### Пользователи
- `POST /users` - Создать пользователя
- `GET /users/{user_id}` - Получить информацию о пользователе
- `GET /analysis/user/{user_id}/devices` - Анализ всех устройств пользователя
- `GET /analysis/user/{user_id}/devices/last-24h` - Анализ за 24 часа

## Примеры использования

### Создание устройства
```bash
curl -X POST "http://localhost:8000/devices" \
  -H "Content-Type: application/json" \
  -d '{"device_id": "device_001", "name": "Sensor Room 1"}'
```

### Добавление показания
```bash
curl -X POST "http://localhost:8000/devices/device_001/readings" \
  -H "Content-Type: application/json" \
  -d '{"x": 45.5, "y": 32.1, "z": 28.9}'
```

### Анализ показаний
```bash
curl -X GET "http://localhost:8000/analysis/device/device_001"
```

### Анализ за период
```bash
curl -X GET "http://localhost:8000/analysis/device/device_001?start_time=2024-01-01T00:00:00&end_time=2024-01-31T23:59:59"
```

## Нагрузочное тестирование

### Запуск с помощью Locust

1. **Установка Locust** (если не установлен):
   ```bash
   pip install locust
   ```

2. **Запуск тестирования**:
   ```bash
   locust -f tests/load_test.py --host=http://localhost:8000 --users=100 --spawn-rate=10
   ```

3. **Веб-интерфейс** (автоматически открывается):
   - Адрес: `http://localhost:8089`
   - Настройте параметры нагрузки через UI

### Тестовые сценарии

Load test включает следующие операции:

| Операция | Вес | Описание |
|----------|------|---------|
| add_device_reading | 5 | Добавление показания устройства |
| get_device_readings | 3 | Получение показаний |
| analyze_device_all_time | 4 | Анализ за всё время |
| analyze_device_last_24h | 3 | Анализ за 24 часа |
| analyze_device_last_7d | 2 | Анализ за 7 дней |
| create_device | 2 | Создание нового устройства |
| list_devices | 1 | Получение списка устройств |
| get_single_device | 1 | Получение информации об устройстве |
| create_user | 2 | Создание пользователя |
| health_check | 1 | Проверка здоровья |

## Результаты нагрузочного тестирования

- Все итоги хранятся в файле `Locust.html`.

## Публикация на GitHub

```bash
git init
git remote add origin https://github.com/Ostap2002-arch/GPN_Changellenge.git
git add .
git commit -m "Prepare project for GitHub deployment"
git branch -M main
git push -u origin main
```




