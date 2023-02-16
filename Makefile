init:
    git config --local core.hooksPath .githooks
	export PIPENV_VENV_IN_PROJECT
	pip install pipenv
	pipenv install
