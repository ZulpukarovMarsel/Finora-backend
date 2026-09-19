# Finora API
## Стек

- **FastAPI** — веб-фреймворк, автогенерация OpenAPI/Swagger
- **SQLAlchemy 2.0** (`Mapped` / `mapped_column`) — ORM
- **Alembic** — миграции схемы БД
- **PostgreSQL 16** — база данных
- **JWT (python-jose) + passlib/bcrypt** — авторизация, т.к. бэкенд
  многопользовательский (нужно для синхронизации между устройствами)
- **Docker Compose** — `api` + `db` сервисы

## Быстрый старт

```bash
cp .env.example .env
# при желании отредактируйте .env (особенно SECRET_KEY для прода)

docker compose up --build
```

Это поднимет Postgres, применит миграции (`alembic upgrade head`) и
запустит API на `http://localhost:8000`.

Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

## Миграции

Дальше при каждом изменении моделей в `app/models/`:

```bash
docker compose run --rm api alembic revision --autogenerate -m "описание изменений"
docker compose run --rm api alembic upgrade head
```

## Структура

```
app/
  core/           # config, DB session, security (JWT/hash)
  models/         # SQLAlchemy-модели, 1:1 с SwiftData-моделями iOS-клиента
  schemas/        # Pydantic-схемы запросов/ответов
  services/       # FinanceService — вся денежная логика в одном месте,
                   # зеркалирует iOS FinanceService (баланс никогда не
                   # меняется напрямую в роутерах)
  api/
    deps.py       # get_current_user (JWT)
    routers/      # по одному роутеру на домен
  main.py
alembic/          # миграции
```

## Домены API (`/api/v1/...`)

| Роутер | Префикс | Что покрывает |
|---|---|---|
| auth | `/auth` | регистрация, логин, `/auth/me` |
| finance | `/finance` | кошелёк, категории, транзакции |
| savings | `/savings` | копилки, пополнение/снятие |
| credits | `/credits` | кредиты, платежи |
| recurring-expenses | `/recurring-expenses` | регулярные расходы + подтверждение |
| tasks | `/tasks` | задачи, будильники, перенос |
| habits | `/habits` | привычки, отметка выполнения, streak |
| water | `/water` | цель, приёмы воды, напоминания |
| nutrition | `/nutrition` | продукты и приёмы пищи |
| books | `/books` | книги, сессии чтения, главы, итоги |
| learning | `/learning` | цели обучения, немецкие слова, математика |
| gamification | `/gamification` | XP, профиль, итоги дня |

Все эндпоймы (кроме `/auth/register` и `/auth/login`) требуют заголовок
`Authorization: Bearer <token>`, полученный при регистрации/логине.

## Локальная разработка без Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# нужен локальный Postgres или измените DATABASE URL на sqlite для теста:
# в app/core/config.py временно замените SQLALCHEMY_DATABASE_URI

alembic upgrade head
uvicorn app.main:app --reload
```
