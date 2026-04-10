# TRPM-LIMS developer & ops entrypoints.
#
# Usage: `make <target>`. Run `make help` to see all targets.

.PHONY: help install migrate run test coverage lint check deploy-check \
        docker-build docker-up docker-down docker-logs secretkey \
        clean

help:  ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install python dependencies
	pip install -r requirements.txt

migrate:  ## Apply database migrations
	python manage.py migrate

run:  ## Run the development server
	DEBUG=True python manage.py runserver 0.0.0.0:8000

test:  ## Run the test suite
	pytest -q

test-smoke:  ## Run smoke tests only
	pytest -q -m smoke

coverage:  ## Run tests with coverage report
	pytest --cov --cov-report=term-missing --cov-report=html

check:  ## Run Django system checks (development mode)
	DEBUG=True python manage.py check

deploy-check:  ## Run Django deploy checks with production-like settings
	@SECRET_KEY=$$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"); \
	SECRET_KEY=$$SECRET_KEY DEBUG=False ALLOWED_HOSTS=localhost \
		python manage.py check --deploy

secretkey:  ## Generate a fresh Django SECRET_KEY
	@python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

docker-build:  ## Build the production Docker image
	docker compose build

docker-up:  ## Start the full stack (app + postgres + redis + nginx)
	docker compose up -d

docker-down:  ## Stop the full stack
	docker compose down

docker-logs:  ## Tail application logs
	docker compose logs -f app

docker-shell:  ## Open a shell inside the running app container
	docker compose exec app bash

clean:  ## Remove python/test caches
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache htmlcov .coverage
