.PHONY: lint test scan

lint:
	python3 -m py_compile inventory/__init__.py inventory/store.py inventory/cli.py tests/__init__.py tests/test_inventory.py

test:
	python3 -m unittest discover -s tests -v

scan:
	python3 -c "import subprocess, sys, os; files = subprocess.check_output(['git', 'ls-files'], text=True).splitlines(); bad = [f for f in files if os.path.basename(f) == '.env' or f.endswith('.pem')]; sys.exit(1 if bad else 0)"
