lint:
	@python3 -m py_compile inventory/store.py
	@python3 -m py_compile inventory/cli.py
	@python3 -m py_compile tests/test_inventory.py

test:
	@python3 -m unittest discover -s tests -v

scan:
	@found=0; for f in $$(git ls-files); do \
		case "$$f" in \
			*.env) echo "ERROR: tracked .env file: $$f"; found=1;; \
			*.pem) echo "ERROR: tracked .pem file: $$f"; found=1;; \
		esac; \
	done; \
	if [ "$$found" -ne 0 ]; then exit 1; fi
