devserver: install-dev-dependencies upgrade-db
	poetry run python -m app.main --host='0.0.0.0' --port=8000 --reload --proxy-headers --forwarded-allow-ips='*'

install-dev-dependencies:
	poetry install --with backend

generate-migration:
	poetry run alembic revision --autogenerate -m "migration"

upgrade-db:
	poetry run alembic upgrade head

reset-db:
	poetry run alembic downgrade base

seed-db:
	poetry run python -m seed_dev
