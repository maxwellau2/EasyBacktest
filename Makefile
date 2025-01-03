test:
	PYTHONPATH=./ pytest tests/

upgrade:
	pip install -r requirements.txt

update-requirements:
	pip freeze > requirements.txt