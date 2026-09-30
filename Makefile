.PHONY: lint test scan

lint:
	@python3 -m py_compile inventory/store.py && \
	 python3 -m py_compile inventory/cli.py && \
	 python3 -m py_compile inventory/__init__.py && \
	 python3 -m py_compile tests/test_inventory.py && \
	 echo "lint OK"

test:
	python3 -m unittest discover -s tests -v

scan:
	@if find . -name .env -o -name '*.pem' | grep -q .; then \
		echo "FAIL: found .env or .pem files"; \
		exit 1; \
	fi
	@echo "scan OK"
