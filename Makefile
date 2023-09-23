PYTHON=python3.11


all: test

test:
	pytest tests/ytests.py 

test-v:
	pytest ymake/ytests.py -s

install-py:
	$(PYTHON) -m pip install dask[distributed] pytest colorama networkx colorlog

run:
	$(PYTHON) tests/ya.py  -vD

y:
	@cd ~/dev/c/YiYiYa && $(PYTHON) ya.py


upload:
	$(PYTHON) -m twine upload dist/* --verbose

dist:
	$(PYTHON) -m build