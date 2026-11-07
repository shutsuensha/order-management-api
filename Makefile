up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy .

migrate:
	uv run python manage.py migrate

check:
	uv run pre-commit run --all-files

run:
	uv run python manage.py runserver

db:
	docker exec -it drf-postgres psql -U postgres -d drf_db
