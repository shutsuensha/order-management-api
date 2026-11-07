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

## Архитектура

```text
Client (Swagger / web / mobile)
                |
                v
API (Django REST Framework + Gunicorn)
          |                    |
          v                    v
   PostgreSQL               Redis
 (orders/catalog/users)    (cache/throttling)
```

Основные сущности: `User` и `Profile`, `Category`, `Product`, `Order` и
`OrderItem`. Товар может относиться к нескольким категориям. Заказ принадлежит
пользователю и содержит позиции со снимком названия и цены товара на момент
покупки.

## Стек

Python 3.14, Django 6, Django REST Framework, PostgreSQL, Redis, Docker Compose, pytest, Ruff.

## Запуск через Docker

1. Скопировать настройки окружения:

   ```bash
   cp .env.example .env
   ```

2. Запустить API, PostgreSQL и Redis:

   ```bash
   make up
   ```

3. Применить миграции внутри API-контейнера и создать администратора:

   ```bash
   docker compose exec api python manage.py migrate
   docker compose exec api python manage.py createsuperuser
   docker compose exec api python manage.py seed_demo
   ```

Swagger доступен по адресу <http://127.0.0.1:8000/api/v1/docs/>.

## Локальный запуск API

Если API запускается из virtualenv, подними только инфраструктуру:

```bash
docker compose up -d postgres redis
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py seed_demo
make run
```

Для Docker используются внутренние имена сервисов `postgres` и `redis`. Для
локального запуска в `.env` используются `localhost`, порты `1112` и `3443`.

## Переменные окружения

Шаблон находится в `.env.example`. Обязательные группы настроек:

- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS` — режим и
  безопасность Django;
- `POSTGRES_*` — подключение к PostgreSQL;
- `REDIS_HOST`, `REDIS_PORT` — подключение к Redis;
- `EMAIL_*`, `DEFAULT_FROM_EMAIL` — отправка писем;
- `JWT_ACCESS_TOKEN_MINUTES`, `JWT_REFRESH_TOKEN_DAYS` — сроки JWT;
- `SENTRY_DSN`, `SENTRY_TRACES_SAMPLE_RATE` — необязательная Sentry-интеграция.

Секреты не добавляются в Git. Для production необходимо использовать длинный
случайный `DJANGO_SECRET_KEY`, отключить `DEBUG` и настроить SMTP.

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

## Ключевые технические решения

- `Order.total` вычисляется сервером из `OrderItem`; итоговая сумма от клиента
  не принимается.
- Создание заказа и изменение остатков выполняются в `transaction.atomic()`.
- `select_for_update()` блокирует товар на время списания stock и защищает от
  конкурентной продажи последнего экземпляра.
- `product_name` и `unit_price` в `OrderItem` сохраняют исторический snapshot
  товара, поэтому изменение каталога не меняет старые заказы.
- JWT используется для аутентификации, а административные операции защищены
  ролью `is_staff`.
- Ownership checks ограничивают чтение и изменение заказа его владельцем.
- Swagger на `/api/v1/docs/` является основной точкой демонстрации API.

## Основной demo-flow

1. Зарегистрировать пользователя через `POST /api/v1/users/`.
2. Получить JWT через `POST /api/v1/token/`.
3. Создать категории и товары от имени администратора.
4. Создать заказ с `items` от имени обычного пользователя.
5. Проверить рассчитанный `total`, списание stock и просмотр собственного заказа.
6. Отменить заказ через `POST /api/v1/orders/{id}/cancel/` и проверить возврат
   остатка.

## Проверки

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Это учебный проект, поэтому он не претендует на production-ready реализацию платёжных операций, складского учёта или сложной бизнес-логики.
