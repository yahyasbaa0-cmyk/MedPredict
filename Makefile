COMPOSE ?= docker compose
EXEC ?= $(COMPOSE) exec -T
SHELL_EXEC ?= $(COMPOSE) exec
BACKEND ?= backend
AI_SERVICE ?= ai_service
ADMIN_USERNAME ?= admin
ADMIN_EMAIL ?= admin@example.com
ADMIN_PASSWORD ?= admin

.PHONY: help setup up build wait-db migrate migrations admin seed train-ai logs ps down restart clean test backend-shell ai-shell frontend-shell urls

help:
	@echo "MedPredict commands"
	@echo ""
	@echo "  make setup          Build, start, migrate, create admin, seed demo data, train AI"
	@echo "  make up             Start all services in the background"
	@echo "  make build          Build all Docker images"
	@echo "  make wait-db        Wait until Postgres accepts connections"
	@echo "  make migrate        Apply Django migrations"
	@echo "  make migrations     Generate Django migrations for local apps"
	@echo "  make admin          Create default admin user if missing"
	@echo "  make seed           Load demo data with backend/seed_data.py"
	@echo "  make train-ai       Train the AI model artifacts"
	@echo "  make logs           Follow service logs"
	@echo "  make ps             Show service status"
	@echo "  make down           Stop services"
	@echo "  make clean          Stop services and remove volumes"
	@echo "  make test           Run backend tests"
	@echo ""
	@echo "Default admin: $(ADMIN_USERNAME) / $(ADMIN_PASSWORD)"

setup: build up wait-db migrate admin seed train-ai urls

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

wait-db:
	@echo "Waiting for Postgres..."
	@until $(COMPOSE) exec -T db pg_isready -U medpredict_user -d medpredict_db >/dev/null 2>&1; do sleep 2; done
	@echo "Postgres is ready."

migrate:
	$(EXEC) $(BACKEND) python manage.py migrate

migrations:
	$(EXEC) $(BACKEND) python manage.py makemigrations accounts patients appointments consultations prescriptions

admin:
	$(EXEC) $(BACKEND) python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$(ADMIN_USERNAME)').exists() or User.objects.create_superuser('$(ADMIN_USERNAME)', '$(ADMIN_EMAIL)', '$(ADMIN_PASSWORD)')"

seed:
	$(EXEC) $(BACKEND) python seed_data.py

train-ai:
	@echo "AI training is deprecated. Using Groq API."

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

down:
	$(COMPOSE) down

restart: down up

clean:
	$(COMPOSE) down -v

test:
	$(EXEC) $(BACKEND) python manage.py test

backend-shell:
	$(SHELL_EXEC) $(BACKEND) python manage.py shell

ai-shell:
	@echo "AI Service container has been removed."

frontend-shell:
	$(SHELL_EXEC) frontend sh

urls:
	@echo ""
	@echo "MedPredict is running:"
	@echo "  Frontend:    http://localhost:5173"
	@echo "  Backend API: http://localhost:8000/swagger/"
	@echo ""
	@echo "Login with: $(ADMIN_USERNAME) / $(ADMIN_PASSWORD)"
