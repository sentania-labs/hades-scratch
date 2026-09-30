.PHONY: lint test scan

lint:
	for f in $$(find . -name '*.py' -not -path './.git/*'); do \
		python3 -m py_compile $$f || exit 1; \
	done

test:
	python3 -m unittest discover -s tests -v

scan:
	@if find . -name '.env' -o -name '*.pem' | grep -q .; then \
		echo "ERROR: Found .env or .pem files"; \
		find . -name '.env' -o -name '*.pem'; \
		exit 1; \
	fi
