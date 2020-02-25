# cpd_notebook_imports

I wrote this package to be able to import code from notebooks inside Cloud Pak for Data. It is still in very early development, any feedback is welcome.

## Install:

To install this package, run:
```
pip install git+git://github.com/jkafrouni/cpd_notebook_imports.git
```

## Getting started:

Simply import this package in your notebook. Once imported, you will then be able to import notebooks just by using their name.
```
# enable notebook imports by loading this package:
import cpd_notebook_imports

# then, import code from notebooks just as if they were regular scripts:
from my_other_notebook import my_cool_function

my_cool_function()
```

## Limitations and guidelines:

### Limitations related to python conventions

Python imports cannot contain a space or a dash in the name of the package. By default, any package that has a dash in its name can be imported by replacing the dash or space with an underscore (e.g. for python packages, `import sklearn_pandas`). For notebooks, it's the same, except with one additional limitation:
- Replace any space in the notebook name with `_`
- Avoid using `-` in notebook names. If you do, replace `-` with `_` in the import statement
- The import will most likely not work if the notebook name has a combination of `-` and `_` or `-` and space (that's the additional limitation)

- Imports in python are static: once a package is imported, if its code is modified, importing again won't work. You will need to restart your notebook and import again, or use `importlib.reload(my_other_notebook)`

### Other limitations
- Names of notebooks in CPD are not unique: the import will work only if there is one exact match

## TODO:
- [x] basic usage
- [x] convert `_` to spaces in import statement -> not needed, spaces are replaced by `_` in `.ipynb` files by CPD already
- [x] convert `_` to `-` if necessessary
- [ ] handle mix of `-` and `_`/space
- [ ] support autocomplete
- [ ] handle duplicates
- [ ] refactor code
- [ ] simplify reloads
- [ ] export to pypi