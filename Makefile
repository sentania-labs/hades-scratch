.PHONY: lint test scan

lint:
	@for f in $$(find . -name '*.py' -not -path './.git/*'); do \
		python3 -m py_compile "$$f" || { echo "FAIL: $$f"; exit 1; }; \
	done

test:
	python3 -m unittest discover -s tests -v

scan:
	@if find . -not -path './.git/*' -type f \( -name '.env' -o -name '*.pem' \) | grep -q .; then \
		echo "ERROR: found tracked files matching .env or *.pem"; exit 1; \
	fi
