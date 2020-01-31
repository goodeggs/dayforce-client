ISORT=isort --recursive --skip .venv --skip .venvs --skip .tox

fmt:
	$(ISORT)

test:
	@tox -e py37

dev_install:
	pip3 install --upgrade pip
	pip3 install -e .
	pip3 install -r dev-requirements.txt

sanity_check:
	pip3 list
