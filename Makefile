# Makefile for managing project tasks

# List of phony targets
.PHONY: create-env clean remove-env db pip_install down init_db setup help

VENV_NAME=myenv

ifeq ($(OS),Windows_NT)
    SYSTEM=Windows_NT
    VENV_ACTIVATE=.\\$(VENV_NAME)\\Scripts\\activate
    PYTHON=$(VENV_NAME)\\Scripts\\python.exe
    PIP=$(VENV_NAME)\\Scripts\\pip.exe
else
    SYSTEM=$(shell uname -s)
    VENV_ACTIVATE=./$(VENV_NAME)/bin/activate
    PYTHON=$(VENV_NAME)/bin/python3
    PIP=$(VENV_NAME)/bin/pip3
endif

# Create a Python virtual environment
create-env: ## Create a Python virtual environment
	@echo "Creating virtual environment..."
	@if not exist $(VENV_NAME) python -m venv $(VENV_NAME)

# Cleanup
clean: ## Remove __pycache__ directory
	@echo "Removing byte-compiled python files..."
	rmdir /s /q __pycache__

# Remove the Python virtual environment
remove-env: clean ## Remove the Python virtual environment
	@echo "Removing virtual environment..."
	rmdir /s /q $(VENV_NAME)

# Start the database using Docker Compose
db: ## Start the database using Docker Compose
	@echo "Starting the database..."
	docker-compose up -d

# Install project requirements into virtual environment
pip_install: create-env ## Install project requirements
	@echo "Installing project requirements..."
	$(PIP) install -r requirements.txt

# Tear down the Docker containers
down: ## Tear down Docker containers
	@echo "Tearing down the Docker containers..."
	docker-compose down

# Run init using main.py
init_db: create-env ## Run the init script
	@echo "Running init..."
	$(PYTHON) example.py
	@echo "Init completed."

# Start all services
setup: db pip_install ## Start all services
	@echo "Pausing for the database to initialize..."
	@cmd /c "timeout /t 10 /nobreak >nul"
	$(MAKE) init_db

# List all available make commands
help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
