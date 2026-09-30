.PHONY: lint test scan

lint:
	@python3 -m py_compile textstats.py
	@python3 -m py_compile tests/test_textstats.py

test:
	@python3 -m unittest discover -s tests -v

scan:
	@found=0; \
	for f in $$(git ls-files); do \
		case "$$f" in \
			*.env) echo "Found tracked file: $$f"; found=1 ;; \
			*.pem) echo "Found tracked file: $$f"; found=1 ;; \
		esac; \
	done; \
	if [ $$found -ne 0 ]; then exit 1; fi
