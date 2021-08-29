
venv:
	python -m venv venv

deps:
	pip install -e .[tests]

typecheck:
	. venv/bin/activate
	venv/bin/mypy -p smpplib

test:
	. venv/bin/activate
	pytest -v smpplib
