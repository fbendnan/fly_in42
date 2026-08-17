
install:
	uv sync

run:
	uv run main.py config.txt

debug:
	uv run python3 -m pdb main.py config.txt

clean:
	rm -rf __pycache__ parse/__pycache__ algo/__pycache__ helpers/__pycache__ .mypy_cache

lint:
	flake8 . --exclude=.venv
	mypy . --warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	flake8 . --exclude=.venv
	mypy . --strict