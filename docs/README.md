
Propertime docs
--------------

Docs are generated directly from the docstrings using Sphinx.

The required Python depencies are as follows:

    pip install Sphinx==3.5.2 sphinx-rtd-theme==0.5.1 Jinja2==3.0.3

To build the docs, run:

    make clean && make html

To re-generate autosummary-generated files (nearly all the *.rst files in this directory, change `autosummary_generate` to `True` in `config.py`. Watch out that the order will be re-set to alphabetical (see https://github.com/sphinx-doc/sphinx/issues/5379).


