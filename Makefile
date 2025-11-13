test:
	PYTHONPATH=./ pytest tests/

build:
	@./build.sh

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
	@rm -rf easy_backtest.egg-info
	@rm -rf __pycache__
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✓ Clean complete"

upgrade:
	pip install -r requirements.txt

update-requirements:
	pip freeze > requirements.txt

install:
	pip install -e .

.PHONY: test build clean upgrade update-requirements install