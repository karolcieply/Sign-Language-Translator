local_setup: install_requirements activate pre_commit

healthcheck,: install_requirements healthcheck_docker healthcheck_env

healthcheck: install_requirements healthcheck_docker healthcheck_env

sign_language_translator: healthcheck
	docker compose -f docker-compose.yaml up --build frontend backend -d

backend: healthcheck, 
		docker compose -f docker-compose.yaml up --build backend -d

frontend: healthcheck
		docker compose -f docker-compose.yaml up --build frontend -d

OSFLAG 				:=
ifeq ($(OS),Windows_NT)
 OSFLAG = WINDOWS
else
 UNAME_S := $(shell uname -s)
 ifeq ($(UNAME_S),Linux)
  OSFLAG = LINUX
 endif
 ifeq ($(UNAME_S),Darwin)
  OSFLAG = OSX
 endif
endif

healthcheck_docker:
	docker info

healthcheck_env:
ifeq ($(OSFLAG), WINDOWS)
	powershell -Command "Test-Path -Path '.env'"
else
	test -f ".env"
endif

install_requirements:
	poetry config --local virtualenvs.in-project true
	poetry install --no-root

activate:
	poetry shell

pre_commit:
	poetry run pre-commit install

ruff:
	poetry run ruff check --fix && poetry run ruff format