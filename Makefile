all: testing docs

clean:
	find -name '*.pyc'|xargs rm -f; rm -rf html

docs: html/index.html

html/index.html:
	doxygen Doxyfile

testing:
	python -m unittest discover -p "*.py" -v

