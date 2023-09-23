PYTHON=python3.11


all: test

test:
	pytest tests/ytests.py 

test-v:
	pytest ymake/ytests.py -s

install-py:
	$(PYTHON) -m pip install build twine pytest colorama networkx colorlog #dask[distributed]

run:
	$(PYTHON) tests/ya.py  -vD

y:
	@cd ~/dev/c/YiYiYa && $(PYTHON) ya.py -vD


upload:
	$(PYTHON) -m twine upload dist/* --verbose

dist: ymake/*.py
	rm -rf dist
	$(PYTHON) -m build