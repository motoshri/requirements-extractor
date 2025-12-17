.PHONY: help build run test clean docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all services
	@echo "Building all services..."
	@cd gateway && go build -o ../bin/gateway .
	@cd auth-service && go build -o ../bin/auth-service .
	@cd voice-service && go build -o ../bin/voice-service .
	@cd storage-service && go build -o ../bin/storage-service .
	@cd user-service && go build -o ../bin/user-service .
	@echo "Build complete!"

run: ## Run all services (requires build first)
	@echo "Starting all services..."
	@./bin/gateway &
	@./bin/auth-service &
	@./bin/voice-service &
	@./bin/storage-service &
	@./bin/user-service &
	@echo "All services started. Use 'make stop' to stop them."

stop: ## Stop all running services
	@pkill -f gateway || true
	@pkill -f auth-service || true
	@pkill -f voice-service || true
	@pkill -f storage-service || true
	@pkill -f user-service || true
	@echo "All services stopped."

test: ## Run all tests
	@echo "Running tests..."
	@cd gateway && go test ./...
	@cd auth-service && go test ./...
	@cd voice-service && go test ./...
	@cd storage-service && go test ./...
	@cd user-service && go test ./...

clean: ## Clean build artifacts
	@rm -rf bin/
	@echo "Clean complete!"

docker-up: ## Start all services with Docker Compose
	docker-compose up -d
	@echo "Services started. Use 'make docker-down' to stop."

docker-down: ## Stop all Docker services
	docker-compose down
	@echo "Services stopped."

docker-logs: ## View Docker logs
	docker-compose logs -f


