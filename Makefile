.PHONY: lint test scan

lint:
	python3 -m py_compile slug.py tests/test_slug.py

test:
	python3 -m unittest discover -s tests -v

scan:
	! git ls-files | grep -E '(^|/)\.env$$|\.pem$$'
