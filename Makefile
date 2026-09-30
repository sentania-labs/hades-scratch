.PHONY: lint test scan

lint:
	@find . -name '*.py' -not -path './.git/*' -print0 | xargs -0 python3 -m py_compile

test:
	python3 -m unittest discover -s tests -v

scan:
	@if git ls-files | grep -E '(^|/)\.env$|\.pem$$' > /dev/null; then \
		echo "FAIL: tracked files match .env or .pem patterns"; \
		exit 1; \
	fi
