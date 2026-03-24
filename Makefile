.PHONY: venv install run test clean up down restart logs open build

# ── Local development ─────────────────────────────────────────────────────────

# Create virtual environment
venv:
	python3 -m venv venv
	@echo "Virtual environment created."
	@echo "Activate with: source venv/bin/activate  (macOS/Linux)"
	@echo "              venv\\Scripts\\activate       (Windows)"

# Install dependencies (run after activating venv)
install:
	pip install -r requirements.txt

# Run the app locally
run:
	streamlit run app.py

# Run unit tests
test:
	PYTHONPATH=. pytest tests/ -v

# Remove virtual environment and cached files
clean:
	rm -rf venv __pycache__ .pytest_cache dist build
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# ── Docker ────────────────────────────────────────────────────────────────────

# Build and start container, then open browser
up: build
	docker compose up -d
	@echo "Waiting for Loki Viewer to be ready..."
	@sleep 2
	@$(MAKE) open

# Stop and remove container
down:
	docker compose down

# Rebuild and restart container
restart: down up

# Build Docker image
build:
	docker compose build

# Tail container logs
logs:
	docker compose logs -f lokiviewer

# Open app in browser (macOS and Linux)
open:
	@if [ "$$(uname)" = "Darwin" ]; then \
		open http://localhost:8501; \
	else \
		xdg-open http://localhost:8501 2>/dev/null || echo "Open http://localhost:8501 in your browser"; \
	fi
