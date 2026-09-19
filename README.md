# Finora API

FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL backend for the Finora app.
The schema mirrors the SwiftData models 1:1 so the iOS `APIRepository`
(when you build it) maps cleanly onto these endpoints.

## Что реально протестировано

Перед сборкой в архив это API было end-to-end проверено на настоящем
PostgreSQL 16 (не на моках): регистрация/логин с JWT, кошелёк и
доходы/расходы через `FinanceService` (включая отказ при нехватке
средств), копилки с депозитом, кредиты с платежами, задачи и их
переключение, привычки со streak, вода, книги с сессией чтения и
обновлением текущей страницы, обучение (немецкие слова + математика),
начисление XP и дневная сводка, а также проверка отказа при неверном
пароле и без токена авторизации. Миграция Alembic сгенерирована и
применена на этой же базе без ошибок.

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

Первая миграция (`alembic/versions/b1a742b1d01c_initial_schema.py`) уже
сгенерирована и протестирована — создана через `alembic revision --autogenerate`
против реального PostgreSQL 16 и применена (`alembic upgrade head`) без ошибок,
все 28 таблиц и индексы создаются корректно. При обычном `docker compose up`
она применится автоматически (`alembic upgrade head` встроена в entrypoint
`api`-сервиса).

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

## Связь с iOS-клиентом

Ничего в SwiftUI-коде клиента менять не нужно прямо сейчас — приложение
продолжает работать оффлайн-first на SwiftData. Когда будете подключать
этот бэкенд, создайте `APIFinanceRepository`, `APITaskRepository` и т.д.,
реализующие те же протоколы из `Data/Repositories/RepositoryProtocols.swift`,
и делающие `URLSession`-запросы к этим эндпоинтам вместо SwiftData —
экраны (View) менять не придётся.
