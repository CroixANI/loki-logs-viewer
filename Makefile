.PHONY: venv install run test clean

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
