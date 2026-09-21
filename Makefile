up:
	docker compose up -d

down:
	docker compose down

check:
	uv run pre-commit run --all-files