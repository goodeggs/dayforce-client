ISORT=isort --recursive --skip .venv --skip .venvs --skip .tox

fmt:
	@black .
	@$(ISORT)

test:
	@tox -e py37

clean:
	@rm -rf .tox .mypy_cache dist

dev_install:
	pip3 install --upgrade pip
	pip3 install -e .
	pip3 install -r dev-requirements.txt

sanity_check:
	pip3 list
