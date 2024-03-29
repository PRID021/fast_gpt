build:
	docker compose build

start:
	docker compose up -d

stop:
	docker compose down

lint:
	black .
	isort .

crawling_data:
	docker compose exec server poetry run python app/ingest.py

prod_crawling:
	poetry run python app/ingest.py

clear_data:
	docker compose exec server poetry run python app/clear_data.py

prod_clear_data:
	poetry run python app/clear_data.py

create_migration:
	docker compose exec server poetry run alembic revision -m "${name}"

migrate:
	docker compose exec server poetry run alembic upgrade head

prod_migrate:
	poetry run alembic upgrade head

downgrate:
	docker compose exec server poetry run alembic downgrade -1

pip_clear:
	pip freeze --exclude-editable | xargs pip uninstall -y
poetry_install:
	pip install langchainhub
	pip install poetry
	poetry lock --no-update
	poetry install
	poetry export -f requirements.txt --output requirements.txt