.PHONY: demo up down logs health clean

# Quick demo - one command to start everything
demo:
	@./scripts/demo-up.sh

# Standard commands
up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

health:
	@curl -s http://localhost:8090/health | jq . || echo "API not ready"

# Cleanup (removes volumes too!)
clean:
	docker compose down -v
	@echo "✅ Cleaned up containers and volumes"

# Status
status:
	@docker compose ps
