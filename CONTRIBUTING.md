# Contributing to LTIAuthenticator

Welcome! As a [Jupyter](https://jupyter.org) project, you can follow the [Jupyter contributor guide](https://jupyter.readthedocs.io/en/latest/contributing/content-contributor.html).

Make sure to also follow [Project Jupyter's Code of Conduct](https://github.com/jupyter/governance/blob/master/conduct/code_of_conduct.md) for a friendly and welcoming collaborative environment.

## Setting up a development environment

LTIAuthenticator requires Python >= 3.6.

1. Clone the repo:

   ```bash
   git clone https://github.com/jupyterhub/jupyterhub
   ```

2. Do a development install with `pip`:

   ```bash
   cd ltiauthenticator
   python3 -m pip install --editable .
   ```

3. Install the development requirements, which include things like linting and testing tools:

   ```bash
   python3 -m pip install -r dev-requirements.txt
   ```

4. Set up pre-commit hooks for automatic code formatting and linting:

   ```bash
   pre-commit install
   ```

   You can also invoke the pre-commit hook manually at any time with:

   ```bash
   pre-commit run
   ```

## Contributing

The LTIAuthenticator has adopted automatic code formatting so you shouldn't need to worry too much about your code style.
As long as your code is valid, the pre-commit hook should take care of how it should look. You can invoke the pre-commit hook by hand at any time with:

```bash
pre-commit run
```

which should run any autoformatting on your code and tell you about any errors it couldn't fix automatically. You may also install [black integration](https://github.com/psf/black#editor-integration) into your text editor to format code automatically.

If you have already committed files before setting up the pre-commit hook with `pre-commit install`, you can fix everything up using `pre-commit run --all-files`. You need to make the fixing commit yourself after that.

## Testing

It's a good idea to write tests to exercise any new features, or that trigger any bugs that you have fixed to catch regressions.

From the root of the repo, you can run the tests with:

```bash
pytest -v
```

If you want to just run certain tests, check out the [pytest docs](https://pytest.readthedocs.io/en/latest/usage.html)
for how pytest can be called. For example:

```bash
pytest -v -k spawn ltiauthenticator/tests/test_lti.py
```

## Commit Messages, Changelog, and Releases

This project includes `pre-commit` hooks configured to run `black`, `flake8`, and `pip-compile` before running and completing the `git commit ...` command. If these tools do not run when running the `git add ...` and `git commit ...` commands, make sure you install the pre-commit hooks with `pre-commit install`.

### For Contributors

This project uses Semantic Versioning with Conventional Commits to track major, minor, and patch releases. The `npm run release` command automates [CHANGLOG.md](./CHANGELOG.md) updates and release version metadata.

Once a new version is released, assets should be published with the new tag, such as docker images, pip/npm packages, and GitHub repo release tags.

For the most part, contributors do not need to worry about commit message formats, since all commits from a Pull Request are squashed and merged before merging to `main`. Commit messages are updated to the standard format during this step.

### For Maintainers

When squashing and merging to the `main` branch, use the following format to provide consistent updates to the `CHANGELOG.md` file:

    <Commit Type>(scope): <Merge Description>

- `Merge Description` should initiate with a capital letter, as it provides the changelog with a standard sentence structure.

- `Scope` is used to define what is being updated. Our current scopes include:

1. lti11
3. lti13

- `Commit Types` are listed below:

| Commit Type | Commit Format |
| --- | --- |
| Chores | `chore` |
| Documentation | `docs` |
| Features | `feat` |
| Fixes | `fix` |
| Refactoring | `refactor` |

Use the `BREAKING CHANGE` in the commit's footer if a release has a breaking change.

Examples:

- Commit a new feature:

    ```
    feat(workspace): Publish static notebooks with live widgets
    ```

- Commit a bug fix:

    ```
    fix(core): Allow students to open submitted assignments from grades section
    ```

- Commit a version with a breaking change:

    ```
    feat(core): Deprecate observer role from group memberships

    BREAKING CHANGE: `extends` key in config file is now used for extending other config files
    ```
