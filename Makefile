# Default make target
init: hwstats

# Make target to build a development environment
dev:
	@echo "Building development environment"
	export PIPENV_VENV_IN_PROJECT
	pip install pipenv
	pipenv install --dev
	pipenv run pip install --upgrade pip
	pipenv run pre-commit install
	pipenv run pre-commit autoupdate
	pipenv shell

# Make target to build a code release
hwstats: clean
	@echo "Building code release"
	pipenv lock
	pipenv sync
	pipenv requirements > requirements.txt

	@echo "Building executable"
	pyinstaller \
	 	--add-data hwstats/templates:templates \
		--add-data hwstats/static:static  \
		--noconfirm \
		--name hwstats \
		--onefile \
		hwstats/cli.py

	@echo "   Build complete!"
	@echo "   Executable is: ${PWD}/dist/hwstats"

clean:
	@echo "Cleaning up old build data..."
	rm -rf dist
