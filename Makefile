up:
	docker compose up -d

down:
	docker compose down

check:
	uv run pre-commit run --all-files

run:
	uv run python manage.py runserver