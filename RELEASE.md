# How to make a release

`jupyterhub-ltiauthenticator` is a package available on [PyPI][]. These are
instructions on how to make a release.

## Pre-requisites

- Push rights to [github.com/jupyterhub/ltiauthenticator][]

## Steps to make a release

1. Create a PR updating `docs/source/changelog.md` with [github-activity][] and
   continue only when its merged. Some guidance is available in a
   [jupyterhub/team-compass issue][].

1. Checkout main and make sure it is up to date.

   ```shell
   git checkout main
   git fetch origin main
   git reset --hard origin/main
   ```

1. Update the version, make commits, and push a git tag with `tbump`.

   ```shell
   pip install tbump
   tbump --dry-run ${VERSION}

   # run
   tbump ${VERSION}
   ```

   Following this, the [CI system][] will build and publish a release.

1. Reset the version back to dev, e.g. `2.0.1.dev0` after releasing `2.0.0`.

   ```shell
   tbump --no-tag ${NEXT_VERSION}.dev0
   ```

[jupyterhub/team-compass issue]: https://github.com/jupyterhub/team-compass/issues/563
[github-activity]: https://github.com/executablebooks/github-activity
[github.com/jupyterhub/ltiauthenticator]: https://github.com/jupyterhub/ltiauthenticator
[pypi]: https://pypi.org/project/jupyterhub-ltiauthenticator/
[ci system]: https://github.com/jupyterhub/ltiauthenticator/actions/workflows/publish.yaml
