# 📅 Booking Service API (Backend)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)

> Проект ориентирован на production-подход и демонстрацию архитектурных навыков backend-разработки.

Асинхронный API для записи клиентов к мастерам (салон, услуги и т.д.) с поддержкой фоновых задач, сложной бизнес-логики и тестирования.

---

## 🚀 Функционал

### 🔐 Auth & Security
* JWT авторизация  
* Роли: пользователь / администратор  

---

### 👤 Пользователи
* Профиль пользователя  
* Telegram ID для уведомлений  
* Система лояльности (скидки)  

---

### 💇 Услуги и мастера
* Каталог услуг  
* Связь мастер ↔ услуга (many-to-many)  
* Цена и длительность услуги  

---

### 📅 Рабочее расписание
* Настройка рабочих дней  
* Ограничение по времени работы  
* Проверка доступности перед записью  

---

### ⏱ Свободные слоты
* Расчет на основе:
  - графика мастера  
  - длительности услуги  
  - существующих записей  
* Защита от пересечений (race condition safe)  

---

### 🧾 Записи (Booking System)

**Flow создания записи:**
1. Выбор услуги  
2. Выбор мастера  
3. Выбор даты  
4. Получение свободных слотов  
5. Создание записи  

**Валидации:**
* нельзя записаться в прошлое  
* нельзя выйти за рабочие часы  
* нельзя пересекать другие записи  
* слот должен соответствовать длительности услуги  

---

### 🔄 FSM статусы

- `created → confirmed → done`  
- `created → cancelled`  
- `confirmed → cancelled`  
* Контроль переходов  
* Защита от некорректных действий  

---

### ❌ Отмена записи
* Отмена пользователем  
* Отмена запланированных задач (Celery revoke)  

---

### ⚙️ Admin API
* Подтверждение записи  
* Отмена записи  
* Завершение записи  
* Контроль FSM  

---

### 🔔 Уведомления (Celery + Redis)
* Уведомление о новой записи  
* Уведомление об отмене  
* Массовая рассылка  
* Напоминания:
  - за 24 часа  
  - за 2 часа  

---

### 📩 Telegram
* Уведомления пользователям  
* Уведомления администраторам  
* Отправка через Celery  

---

### 🧪 Тестирование
* pytest + httpx  
* Проверка:
  - FSM  
  - бизнес-логики  
  - edge cases  
  - race conditions  

---

### 🐳 Инфраструктура
* PostgreSQL  
* Redis  
* Celery worker  
* Docker Compose  

## 🛠 Стек технологий

* **Язык:** Python 3.10+
* **Framework:** FastAPI (Async)
* **ORM:** SQLAlchemy (async + sync)
* **Миграции:** Alembic
* **БД:** PostgreSQL
* **Фоновые задачи:** Celery + Redis
* **Контейнеризация:** Docker & Docker Compose
* **Тесты:** Pytest + httpx (для асинхронных запросов)

## 📂 Структура проекта

* **alembic/**
  - История миграций базы данных  

* **app/**
  - Основное приложение  

  Внутри:
  - **routers/**
    - `admin/` — административные эндпоинты  
    - `public/` — пользовательские эндпоинты  
  - **auth/** — аутентификация и безопасность (JWT)  
  - **database.py** — настройка БД (async + sync)  
  - **models/** — ORM модели (SQLAlchemy)  
  - **schemas/** — Pydantic схемы  
  - **services/** — бизнес-логика  
  - **usecases/** — orchestration слой (сценарии)  
  - **tasks/** — Celery задачи  
  - **main.py** — точка входа  

* **tests/**
  - Интеграционные тесты  
  - FSM тесты  
  - Проверка race conditions  
  - `conftest.py` — фикстуры  

* **docker-compose.yml**
  - PostgreSQL + Redis + Celery  

* **Dockerfile**
  - Сборка приложения  

---

## ⚙️ Установка и запуск

### 🔧 Локальный запуск

* Клонировать репозиторий:
```bash
git clone <URL>
cd booking-service
```

* Создать виртуальное окружение:
```bash
python -m venv venv
```

* Активировать:
```bash
# Linux / MacOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

* Установить зависимости:
```bash
pip install -r requirements.txt
```

* Настроить переменные:
```bash
cp .env.example .env
```

* Применить миграции:
```bash
alembic upgrade head
```

* Запустить сервер:
```bash
uvicorn app.main:app --reload
```

---

### 🐳 Docker запуск (рекомендуется)

* Поднять сервисы:
```bash
docker-compose up --build -d
```

* Применить миграции:
```bash
docker-compose exec app alembic upgrade head
```

Поднимаются сервисы:

* PostgreSQL  
* Redis  
* FastAPI  
* Celery worker  

---

## 📖 Документация API

* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)  

---

## 🔄 Пример бизнес-сценария

1. Пользователь выбирает услугу  
2. Получает список мастеров  
3. Выбирает дату  
4. Получает свободные слоты  
5. Создает запись  

Система:

* Валидирует данные  
* Сохраняет запись  
* Отправляет уведомления  
* Планирует напоминания (Celery)  

Администратор:

* Подтверждает запись  
* Завершает или отменяет  

---

## 🔐 Переменные окружения

```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/booking
JWT_SECRET_KEY=super-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

---

## 🧪 Тестирование

* Интеграционные тесты  
* Проверка бизнес-логики  
* FSM переходы  
* Race conditions  

Запуск:
```bash
pytest -v
```

---

## ⚠️ Ограничения

* Нет UI (только API)  
* Telegram без webhook сервера  
* Нет платежных интеграций  

---

## 🛣 Roadmap

* [ ] WebSocket уведомления  
* [ ] Rate limiting (Redis)  
* [ ] Кэширование слотов  
* [ ] CI/CD (GitHub Actions)  
* [ ] Мониторинг (Prometheus + Grafana)  

---

## 📄 Лицензия

* MIT License