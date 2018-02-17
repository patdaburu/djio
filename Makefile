.DEFAULT_GOAL := build
.PHONY: build publish flightcheck docs venv


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

#venv :
	# virtualenv --python python3.6 venv

venv:
	conda env create -f environment.yml
	# To remove the environment: conda remove --name djio --all

install:
	pip install -r requirements.txt

