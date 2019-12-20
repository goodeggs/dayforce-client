isort:
	isort --recursive

flake8:
	flake8 . --ignore=E501,E722 --count --statistics

dev_install:
	pip3 install --upgrade pip
	pip3 install -e .
	pip3 install -r dev-requirements.txt

sanity_check:
	pip3 list
