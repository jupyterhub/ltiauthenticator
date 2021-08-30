# About the documentation

This documentation is automatically built on each commit [as configured on
ReadTheDocs](https://readthedocs.org/projects/ltiauthenticator/) and
in the `.readthedocs.yml` file, and made available on
[ltiauthenticator.readthedocs.io](https://ltiauthenticator.readthedocs.io/en/latest/).

## Local documentation development

```shell
cd docs
pip install -r requirements.txt
```

```shell
# automatic build and livereload enabled webserver
make devenv

# automatic check of links validity
make linkcheck
```
