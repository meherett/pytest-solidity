install: clean
	-pip freeze | xargs pip uninstall -y
	pip install -e .

test: install
	pytest tests/

# Verify our example project
.PHONY: example
example: install
	pytest --cobra example/MetaCoin.sol

upload: test example
	pip install twine
	python setup.py sdist
	twine upload dist/*

# Checks dry run, then prompts to execute
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf pytest_cobra.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
