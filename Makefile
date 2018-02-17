.DEFAULT_GOAL := build
.PHONY: build publish flightcheck docs venv
VENV_NAME = djio


build: coverage flightcheck
	@echo No python build is defined.

freeze:
	pip freeze > requirements.txt

coverage: test
	mkdir -p docs/build/html
	coverage html

docs: coverage
	mkdir -p docs/source/_static
	mkdir -p docs/source/_templates
	cd docs && $(MAKE) html

flightcheck:
	python setup.py sdist

publish:
	python setup.py sdist upload -r pypi

clean :
	rm -rf dist \
	rm -rf docs/build \
	rm -rf *.egg-info
	coverage erase

test:
	py.test --cov . tests/

venv :
	virtualenv --python python3.6 venv

conda:
	conda env create -f environment.yml
	# To remove the environment: conda remove --name djio --all
	
activate:
	@echo Make cannot do this for you, but you can do the following:
	@echo
	@echo If you are using a local virtual environment:
	@echo     source venv/bin/activate
	@echo
	@echo If your are using a conda virtual environment:
	@echo     source activate $(VENV_NAME)

install:
	pip install -r requirements.txt

