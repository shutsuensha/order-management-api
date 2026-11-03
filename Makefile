up:
	docker compose up -d

down:
	docker compose down

check:
	uv run pre-commit run --all-files

run:
	uv run python manage.py runserver

db:
	docker exec -it drf-postgres psql -U postgres -d drf_db