.PHONY: lint test scan

lint:
	python3 -m py_compile tests/test_experiment_record.py

test:
	python3 -m unittest discover -s tests -v

scan:
	! grep -RP '(access_token|refresh_token|id_token)[[:space:]]*"?[[:space:]]*[:=][[:space:]]*"?[A-Za-z0-9_.-]+' experiments
