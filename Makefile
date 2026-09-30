.PHONY: lint test scan

lint:
	@found=0; \
	for f in $$(find . -name '*.py' -not -path './.git/*'); do \
		python3 -m py_compile "$$f" || exit 1; \
		found=1; \
	done; \
	if [ "$$found" -eq 0 ]; then \
		echo "No .py files found"; exit 1; \
	fi

test:
	python3 -m unittest discover -s tests -v

scan:
	@found=0; \
	for f in $$(git ls-files); do \
		case "$$f" in \
			*.env|*.pem) echo "ERROR: tracked file $$f"; found=1;; \
		esac; \
	done; \
	exit $$found
