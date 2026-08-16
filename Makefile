install:
	uv sync

run:
	uv run main.py config.txt

clean:
	rm -rf __pycache__ parse/__pycache__ algo/__pycache__ helpers/__pycache__

lint:
	flake8 . --exclude=.venv
	mypy . --strict