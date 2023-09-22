all: test

test:
	pytest tests/ytests.py 

test-v:
	pytest ymake/ytests.py -s

install-py:
	pip3 install pytest colorama networkx colorlog

run:
	python3 tests/ya.py 

y:
	@cd ~/dev/c/YiYiYa && python3 ya.py


upload:
	python3 -m twine upload dist/*

dist:
	python3 -m build