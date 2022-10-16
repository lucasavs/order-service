run:
	python3 -m uvicorn app.main:app --reload

lint:
	python3 -m black . --check --exclude /postgres-data
	python3 -m flake8 .

beautify:
	python3 -m black . --exclude /postgres-data

test:
	python3 -m pytest --ignore=postgres-data