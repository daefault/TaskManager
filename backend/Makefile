.PHONY: migrate migrate-up

#Создание миграции - make migrate msg="migration message"
migrate:
	poetry run alembic revision --autogenerate -m "$(msg)"

migrate-up:
	poetry run alembic upgrade head