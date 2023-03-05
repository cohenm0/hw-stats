init:
	export PIPENV_VENV_IN_PROJECT
	pip install pipenv
	pipenv install --dev
	pipenv run pip install --upgrade pip
	pipenv run pre-commit install
	pipenv run pre-commit autoupdate
	pipenv shell
