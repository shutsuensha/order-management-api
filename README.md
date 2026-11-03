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

Swagger доступен по адресу <http://127.0.0.1:8000/api/docs/>.

## Основные endpoint'ы

| Метод | URL | Назначение |
| --- | --- | --- |
| POST | `/api/token/` | получить access/refresh JWT |
| POST | `/api/token/refresh/` | обновить access-токен |
| CRUD | `/api/users/` | пользователи |
| CRUD | `/api/categories/` | категории |
| CRUD | `/api/products/` | товары, только для администратора |
| GET/POST | `/api/orders/` | список и создание собственных заказов |
| GET/PATCH/DELETE | `/api/orders/<id>/` | работа со своим заказом |

Для защищённых запросов передайте заголовок:

```text
Authorization: Bearer <access-token>
```

## Проверки

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Это учебный проект, поэтому он не претендует на production-ready реализацию платёжных операций, складского учёта или сложной бизнес-логики.
