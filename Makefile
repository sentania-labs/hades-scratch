.PHONY: lint test scan

lint:
	for f in $$(/usr/bin/find . -path ./.git -prune -o -name '*.py' -print); do \
		python3 -m py_compile "$$f" || exit 1; \
	done

test:
	python3 -m unittest discover -s tests -v

scan:
	if /usr/bin/find . -path ./.git -prune -o -type f \( -name '.env' -o -name '*.pem' \) -print | grep -q .; then \
		echo "Found prohibited files"; \
		exit 1; \
	fi
