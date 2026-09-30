.PHONY: lint test scan

lint:
	@python3 -m py_compile inventory/__init__.py && \
	 python3 -m py_compile inventory/store.py && \
	 python3 -m py_compile inventory/cli.py && \
	 python3 -m py_compile tests/test_inventory.py

test:
	python3 -m unittest discover -s tests -v

scan:
	@if find . -type f \( -name '.env' -o -name '*.pem' \) | grep -q .; then \
		echo "FAIL: .env or .pem files found"; \
		exit 1; \
	fi
