envup:
	python -m venv ./venv
	source ./venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

envdown:
	rm -rf ./venv
