# Order Management API

Учебный REST API интернет-магазина на Django REST Framework. Проект сделан для практики моделей, сериализаторов, permissions, JWT-аутентификации, фильтрации, оптимизации запросов и API-тестов.

## Возможности

- JWT-аутентификация пользователей;
- CRUD для пользователей, категорий и товаров;
- создание и управление заказами только для текущего пользователя;
- права администратора для управления товарами;
- фильтрация заказов по статусу, поиск по номеру и сортировка по сумме;
- PostgreSQL для данных и Redis для кэша;
- Swagger-документация;
- тесты API на pytest и DRF APIClient.

## Стек

Python 3.14, Django 6, Django REST Framework, PostgreSQL, Redis, Docker Compose, pytest, Ruff.

## Запуск

1. Скопировать настройки окружения:

   ```bash
   cp .env.example .env
   ```

2. Запустить PostgreSQL и Redis:

   ```bash
   make up
   ```

3. Установить зависимости через `uv`, применить миграции и создать администратора:

   ```bash
   uv sync
   uv run python manage.py migrate
   uv run python manage.py createsuperuser
   ```

4. Запустить API:

   ```bash
   make run
   ```

Swagger доступен по адресу <http://127.0.0.1:8000/api/v1/docs/>.

## Основные endpoint'ы

| Метод | URL | Назначение |
| --- | --- | --- |
| GET | `/health/live` | проверка, что приложение запущено |
| GET | `/health/ready` | проверка доступности PostgreSQL и Redis |
| POST | `/api/v1/token/` | получить access/refresh JWT |
| POST | `/api/v1/token/refresh/` | обновить access-токен |
| CRUD | `/api/v1/users/` | пользователи |
| CRUD | `/api/v1/categories/` | категории |
| CRUD | `/api/v1/products/` | товары, только для администратора |
| GET/POST | `/api/v1/orders/` | список и создание собственных заказов |
| GET/PATCH/DELETE | `/api/v1/orders/<id>/` | работа со своим заказом |

Для защищённых запросов передайте заголовок:

```text
Authorization: Bearer <access-token>
```

## Healthchecks и резервные копии

`/health/live` проверяет, что процесс API отвечает и может использоваться
оркестратором для liveness-пробы. `/health/ready` проверяет соединения с
PostgreSQL и Redis; при недоступности зависимости endpoint возвращает `503`.

Для локального backup PostgreSQL:

```bash
mkdir -p backups
docker compose exec -T postgres pg_dump -U postgres -d drf_db \
  > backups/drf_db_$(date +%Y%m%d_%H%M%S).sql
```

В production backup следует выполнять по расписанию, хранить вне хоста с базой,
шифровать и регулярно проверять восстановлением. Пример восстановления локальной
копии:

```bash
cat backups/<backup-file>.sql \
  | docker compose exec -T postgres psql -U postgres -d drf_db
```

## Проверки

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Это учебный проект, поэтому он не претендует на production-ready реализацию платёжных операций, складского учёта или сложной бизнес-логики.
