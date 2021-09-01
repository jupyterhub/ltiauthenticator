# How to make a release

`jupyterhub-ltiauthenticator` is a package [available on PyPI](https://pypi.org/project/jupyterhub-ltiauthenticator/). These are instructions on how to make a release on PyPI. The PyPI release is packaged and published automatically by GitHub Actions when a git tag is pushed.

For you to follow along according to these instructions, you need:

- To have push rights to the [ltiauthenticator GitHub repository](https://github.com/jupyterhub/ltiauthenticator).

## Steps to make a release

1. Update `CHANGELOG.md`

   - Generate a list of PRs using [executablebooks/github-activity](https://github.com/executablebooks/github-activity)

     ```bash
     github-activity --output=github-activity-output.md --heading-level=3 jupyterhub/ltiauthenticator
     ```

   - Visit and label all uncategorized PRs appropriately with: `maintenance`, `enhancement`, `breaking`, `bug`, or `documentation`.
   - Generate a list of PRs again and add it to the changelog.
   - Manually highlight the breaking changes and summarize the release.

1. Once the changelog is up to date, checkout main and make sure it is up to date and clean.

   ```bash
   ORIGIN=${ORIGIN:-origin} # set to the canonical remote, e.g. 'upstream' if 'origin' is not the official repo
   git checkout main
   git fetch $ORIGIN main
   git reset --hard $ORIGIN/main
   # WARNING! This next command deletes any untracked files in the repo
   git clean -xfd
   ```

1. Update the version with `bump2version` (can be installed with `pip install -r dev-requirements.txt`)

   ```bash
   VERSION=...  # e.g. 1.2.3
   bump2version --tag --new-version $VERSION -
   ```

1. Reset the version to the next development version with `bump2version`

   ```bash
   bump2version --no-tag patch
   ```

1. Push your two commits to main along with the annotated tags referencing
   commits on main.

   ```
   git push --follow-tags $ORIGIN main
   ```

## Manually uploading to PyPI

We are using CD with GitHub Actions to automatically update PyPI, but if you want to do it manually when you are on a tagged commit in a otherwise cleaned repository, you can do this.

1. Package the release

   ```bash
   python3 setup.py sdist bdist_wheel
   ```

1. Upload it to PyPI

   ```bash
   twine upload dist/*
   ```
