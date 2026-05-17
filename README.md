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
* Token-based авторизация (токены хранятся в БД)
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

---

## 🛠 Стек технологий

* **Язык:** Python 3.10+
* **Framework:** FastAPI (Async)
* **ORM:** SQLAlchemy (async + sync)
* **Миграции:** Alembic
* **БД:** PostgreSQL
* **Фоновые задачи:** Celery + Redis
* **Контейнеризация:** Docker & Docker Compose
* **Тесты:** Pytest + httpx

---

## 📂 Структура проекта

* **alembic/** — история миграций базы данных
* **app/** — основное приложение
  - **routers/** — эндпоинты (admin, client, webapp)
  - **auth/** — аутентификация и безопасность
  - **database.py** — настройка БД (async + sync)
  - **models/** — ORM модели (SQLAlchemy)
  - **schemas/** — Pydantic схемы
  - **services/** — бизнес-логика
  - **usecases/** — orchestration слой
  - **tasks/** — Celery задачи
  - **telegram_bot/** — Telegram бот (aiogram)
  - **main.py** — точка входа
* **tests/** — интеграционные тесты, FSM тесты, race condition тесты
* **docker-compose.yml** — PostgreSQL + Redis + Celery + FastAPI + Bot
* **Dockerfile** — сборка приложения

---

## ⚙️ Установка и запуск

### 🌐 Важно: нужен туннель для Telegram

Бот работает через Telegram Mini App, которому нужен публичный HTTPS URL.
Перед запуском подними любой туннель (ngrok, cloudflared и т.д.) и получи публичный URL.

Пример с cloudflared:
```bash
cloudflared tunnel --url localhost:8000
```

Пример с ngrok:
```bash
ngrok http 8000
```

Полученный URL (например `https://xxx.trycloudflare.com`) вставь в `.env` как `WEBAPP_URL`.

---

### 🐳 Docker запуск (рекомендуется)

1. Клонировать репозиторий:
```bash
git clone <URL>
cd booking-service
```

2. Создать `.env` файл:
```bash
cp .env.example .env
```

3. Заполнить `.env` (см. раздел ниже)

4. Поднять туннель и вставить URL в `WEBAPP_URL`

5. Запустить:
```bash
docker-compose up --build -d
```

Поднимаются сервисы: PostgreSQL, Redis, FastAPI, Celery worker, Telegram bot

---

### 🔧 Локальный запуск

```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

---

## 🔐 Переменные окружения

В проекте два `.env` файла.

**`.env`** — в корне проекта:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=booking
POSTGRES_HOST=db
POSTGRES_PORT=5432

SECRET_KEY=your-secret-key
TOKEN_TTL_HOURS=24

TELEGRAM_BOT_TOKEN=your-bot-token
WEBAPP_URL=https://your-tunnel-url

REDIS_URL=redis://redis:6379/0
```

**`app/telegram_bot/.env`** — для Telegram бота:
```env
BOT_TOKEN=your-bot-token
WEBAPP_URL=https://your-tunnel-url
```

> ⚠️ `WEBAPP_URL` нужно вставить в оба файла — это публичный HTTPS URL туннеля (ngrok, cloudflared и т.д.)

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

## 🧪 Тестирование

```bash
pytest -v
```

---

## ⚠️ Ограничения

* Нет UI (только API)
* Для работы Telegram бота нужен туннель (ngrok / cloudflared)
* Нет платежных интеграций

---

## 🛣 Roadmap

* [ ] WebSocket уведомления
* [ ] Rate limiting (Redis)
* [ ] Кэширование слотов
* [ ] CI/CD (GitHub Actions)
* [ ] Мониторинг (Prometheus + Grafana)
* [ ] Фотографии услуг и портфолио мастеров (загрузка и хранение изображений)

---

## 📄 Лицензия

MIT License
