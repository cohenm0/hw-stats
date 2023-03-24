init: dev

dev:
	@echo "Building development environment"
	export PIPENV_VENV_IN_PROJECT
	pip install pipenv
	pipenv install --dev
	pipenv run pip install --upgrade pip
	pipenv run pre-commit install
	pipenv run pre-commit autoupdate
	pipenv shell

release:
	@echo "Building code release"
	 pyinstaller \
	 	--add-data hwstats/templates:templates \
		--add-data hwstats/static:static  \
		--noconfirm \
		--name hwstats \
		--onefile \
		hwstats/cli.py
	@echo "Build complete: ${PWD}/dist/hwstats"
