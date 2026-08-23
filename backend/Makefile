.PHONY: migrate migrate-up test-db-create

#Создание миграции - make migrate msg="migration message"
migrate:
	poetry run alembic revision --autogenerate -m "$(msg)"

migrate-up:
	poetry run alembic upgrade head

#Создание бд для тестов
test-db-create:
	docker-compose exec db psql -U postgres -c "CREATE DATABASE test_db;"