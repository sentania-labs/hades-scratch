PYTHON_FILES = inventory/__init__.py inventory/store.py inventory/cli.py tests/test_inventory.py

.PHONY: lint test scan

lint:
	python3 -m py_compile $(PYTHON_FILES)

test:
	python3 -m unittest discover -s tests -v

scan:
	@git ls-files | awk -F/ '$$NF == ".env" || /\.pem$$/ { print; found = 1 } END { exit found }'
