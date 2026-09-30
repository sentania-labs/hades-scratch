.PHONY: lint test scan

lint:
	@find . -name '*.py' -not -path './.git/*' | while read f; do python3 -m py_compile "$$f"; done

test:
	python3 -m unittest discover -s tests -v

scan:
	@found=0; \
	for f in $$(git ls-files); do \
		base=$$(basename "$$f"); \
		if [ "$$base" = ".env" ] || echo "$$f" | grep -q '\.pem$$'; then \
			echo "FAIL: tracked file $$f"; \
			found=1; \
		fi; \
	done; \
	if [ "$$found" -eq 1 ]; then exit 1; fi
