.PHONY: lint test scan

lint:
	for f in $$(find . -name '*.py' -not -path './.git/*'); do \
		python3 -m py_compile "$$f"; \
	done

test:
	python3 -m unittest discover -s tests -v

scan:
	@found=$$(git ls-files | grep -E '(^|/)\.env$|^.*\.pem$$'); \
	if [ -n "$$found" ]; then \
		echo "ERROR: tracked files that should not be tracked:"; \
		echo "$$found"; \
		exit 1; \
	fi
