PYTHON=python3.11


all: test

test:
	pytest tests/ytests.py 

test-v:
	pytest ymake/ytests.py -s

install-py:
	$(PYTHON) -m pip install build twine pytest colorama networkx colorlog diskcache #dask[distributed]

run:
	$(PYTHON) tests/ya.py  -vD

y:
	@cd ~/dev/c/YiYiYa && $(PYTHON) ya.py -vD


upload: dist
	$(PYTHON) -m twine upload dist/* --verbose

dist: ymake/*.py setup.py
	rm -rf dist
	$(PYTHON) -m build

dev: clean
	$(PYTHON) setup.py develop

install:
	$(PYTHON) setup.py install --force

clean:
	$(PYTHON) setup.py clean --all
	$(PYTHON) -m pip uninstall yymake -y