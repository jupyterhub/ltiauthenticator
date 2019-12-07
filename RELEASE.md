# How to make a release

`jupyterhub-ltiauthenticator` is a package [available on
PyPI](https://pypi.org/project/jupyterhub-ltiauthenticator/). These are
instructions on how to make a release on PyPI. The PyPI release is packaged and
published automatically by TravisCI when a git tag is pushed.

For you to follow along according to these instructions, you need:
- To have push rights to the [ltiauthenticator GitHub
  repository](https://github.com/jupyterhub/ltiauthenticator).

## Steps to make a release

1. Update [CHANGELOG.md](CHANGELOG.md) if it is not up to date, and verify
   [README.md](README.md) has an updated output of running `--help`. Make a PR
   to review the CHANGELOG notes.

   To get the foundation of the changelog written, you can install
   [github-activity](https://github.com/choldgraf/github-activity) and run
   `github-activity --kind pr jupyterhub/ltiauthenticator` after setting up
   credentials as described in the project's README.md file.

1. Once the changelog is up to date, checkout master and make sure it is up to date and clean.

   ```bash
   ORIGIN=${ORIGIN:-origin} # set to the canonical remote, e.g. 'upstream' if 'origin' is not the official repo
   git checkout master
   git fetch $ORIGIN master
   git reset --hard $ORIGIN/master
   # WARNING! This next command deletes any untracked files in the repo
   git clean -xfd
   ```

1. Update the version with `bump2version` (can be installed with `pip install -r
   dev-requirements.txt`)

   ```bash
   VERSION=...  # e.g. 1.2.3
   bump2version --tag --new-version $VERSION -
   ```

1. Reset the version to the next development version with `bump2version`

   ```bash
   bump2version --no-tag patch
   ```

1. Push your two commits to master along with the annotated tags referencing
   commits on master.

   ```
   git push --follow-tags $ORIGIN master
   ```

## Manually uploading to PyPI

We are using CD with Travis to automatically update PyPI, but if you want to do
it manually when you are on a tagged commit in a otherwise cleaned repository,
you can do this.

1. Package the release

   ```bash
   python3 setup.py sdist bdist_wheel
   ```

1. Upload it to PyPI

   ```bash
   twine upload dist/*
   ```
