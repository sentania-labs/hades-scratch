.PHONY: lint test scan

PY_FILES := $(shell find . -path ./hades-scratch -prune -o -name 'inventory' -prune -o -name tests -prune -o -name '*.py' -print 2>/dev/null) \
            inventory/store.py \
            inventory/cli.py \
            inventory/__init__.py \
            tests/test_inventory.py

lint:
	for f in inventory/store.py inventory/cli.py inventory/__init__.py tests/test_inventory.py; do \
		python3 -m py_compile $$f || exit 1; \
	done

test:
	python3 -m unittest discover -s tests -v

scan:
	@found=0; \
	for f in $$(git ls-files 2>/dev/null); do \
		case "$$f" in \
			*.env) echo "found tracked .env: $$f"; found=1;; \
			*.pem) echo "found tracked .pem: $$f"; found=1;; \
		esac; \
	done; \
	test $$found -eq 0
