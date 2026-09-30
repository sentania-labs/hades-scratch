.PHONY: lint test scan

lint:
	@find . -name '*.py' -not -path './.git/*' -print0 | xargs -0 python3 -m py_compile

test:
	python3 -m unittest discover -s tests -v

scan:
	@if find . -not -path './.git/*' \( -name '.env' -o -name '*.pem' \) -print | grep -q .; then \
		echo "ERROR: tracked .env or .pem files found"; exit 1; \
	fi
