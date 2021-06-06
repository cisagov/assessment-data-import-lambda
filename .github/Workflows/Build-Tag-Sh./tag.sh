---
 Configuration file the Bandit python security scanner
 https://bandit.readthedocs.io/en/latest/config.html
 This config is applied to bandit when scanning the "tests" tree

 Tests are first included by `tests`, and excluded by `skips`.
 If `tests` is empty, all tests are are conidered included.
@@ -10,4 +11,4 @@ tests:
 - B102

skips:
'# - B101 # skip "assert used" check since assertions are required in pytests
  - B101 # skip "assert used" check since assertions are required in pytests
 12  .coveragerc 
@@ -0,0 +1,12 @@
# This is the configuration for code coverage checks
# https://coverage.readthedocs.io/en/latest/config.html

[run]
source = adi
omit =
branch = true

[report]
exclude_lines =
    __name__ == "__main__":
show_missing = true
 7  .github/CODEOWNERS 
@@ -0,0 +1,7 @@
# Each line is a file pattern followed by one or more owners.

# These owners will be the default owners for everything in
# the repo. Unless a later match takes precedence,
# these owners will be requested for review when someone
# opens a pull request.
*       @dav3r @felddy @jsf9k @mcdonnnj @cisagov/team-ois
 68  .github/workflows/build.yml 
@@ -0,0 +1,68 @@
---
name: build

on: [push]

env:
  PIP_CACHE_DIR: ~/.cache/pip
  PRE_COMMIT_CACHE_DIR: ~/.cache/pre-commit

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v1
      - uses: actions/setup-python@v1
        with:
          python-version: 3.7
      - name: Cache pip test requirements
        uses: actions/cache@v1
        with:
          path: ${{ env.PIP_CACHE_DIR }}
          key: "${{ runner.os }}-pip-test-\
            ${{ hashFiles('**/requirements-test.txt') }}"
          restore-keys: |
            ${{ runner.os }}-pip-test-
            ${{ runner.os }}-pip-
      - name: Cache pre-commit hooks
        uses: actions/cache@v1
        with:
          path: ${{ env.PRE_COMMIT_CACHE_DIR }}
          key: "${{ runner.os }}-pre-commit-\
            ${{ hashFiles('**/.pre-commit-config.yaml') }}"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install --upgrade -r requirements-test.txt
      - name: Run linters on all files
        run: pre-commit run --all-files
  build:
    runs-on: ubuntu-latest
    needs: [lint]
    steps:
      - uses: actions/checkout@v1
      - uses: actions/setup-python@v1
        with:
          python-version: 3.7
      - name: Cache pip build requirements
        uses: actions/cache@v1
        with:
          path: ${{ env.PIP_CACHE_DIR }}
          key: "${{ runner.os }}-pip-build-\
            ${{ hashFiles('**/requirements.txt') }}"
          restore-keys: |
            ${{ runner.os }}-pip-build-
            ${{ runner.os }}-pip-
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip wheel
          pip install --upgrade -r requirements.txt
      - name: Build environment
        run: docker-compose build
      - name: Generate lambda zip
        run: docker-compose up
      - name: Upload artifacts
        uses: actions/upload-artifact@v1
        with:
          name: assessment-data-import
          path: assessment-data-import.zip
 6  .gitignore 
@@ -1,5 +1,7 @@
.python-version
.DS_Store
*.egg-info
__pycache__
.python-version
.coverage
.pytest_cache
.DS_Store
assessment-data-import.zip
 7  .mdl_config.json 
@@ -0,0 +1,7 @@
{
  "MD013": {
    "code_blocks": false,
    "tables": false
  },
  "default": true
}
  41  .pre-commit-config.yaml 
@@ -1,7 +1,11 @@
---
default_language_version:
  # force all unspecified python hooks to run python3
  python: python3

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v2.2.3
    rev: v2.4.0
    hooks:
      - id: check-executables-have-shebangs
      - id: check-json
@@ -23,57 +27,64 @@ repos:
      - id: requirements-txt-fixer
      - id: trailing-whitespace
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.16.0
    rev: v0.19.0
    hooks:
      - id: markdownlint
        # The LICENSE.md must match the license text exactly for
        # GitHub's autorecognition fu to work, so we should leave it
        # alone.
        exclude: LICENSE.md
        args:
          - --config=.mdl_config.json
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.15.0
    rev: v1.18.0
    hooks:
      - id: yamllint
  - repo: https://github.com/detailyang/pre-commit-shell
    rev: 1.0.5
    hooks:
      - id: shell-lint
  - repo: https://gitlab.com/pycqa/flake8
    rev: 3.7.7
    rev: 3.7.9
    hooks:
      - id: flake8
        additional_dependencies:
          - flake8-docstrings
  - repo: https://github.com/asottile/pyupgrade
    rev: v1.17.1
    rev: v1.25.1
    hooks:
      - id: pyupgrade
  # Run bandit on "tests" tree with a configuration
  - repo: https://github.com/PyCQA/bandit
    rev: 1.6.0
    rev: 1.6.2
    hooks:
      - id: bandit
        name: bandit (tests tree)
        files: tests
        args:
          - --config=.bandit.yml
  # Run bandit everything but tests directory
  - repo: https://github.com/PyCQA/bandit
    rev: 1.6.2
    hooks:
      - id: bandit
        name: bandit (everything)
        exclude: tests
  - repo: https://github.com/python/black
    rev: 19.3b0
    rev: 19.10b0
    hooks:
      - id: black
  - repo: https://github.com/ansible/ansible-lint.git
    rev: v4.1.0a0
    rev: v4.1.1a5
    hooks:
      - id: ansible-lint
        # files: molecule/default/playbook.yml
  - repo: https://github.com/antonbabenko/pre-commit-terraform.git
    rev: v1.11.0
    rev: v1.12.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate_no_variables
      - id: terraform_docs
  - repo: https://github.com/IamTheFij/docker-pre-commit
    rev: v1.0.0
    hooks:
      - id: docker-compose-check
  - repo: https://github.com/prettier/prettier
    rev: 1.17.1
    rev: 1.19.1
    hooks:
      - id: prettier
 2  .prettierignore 
@@ -1,3 +1,5 @@
# Already being linted by pretty-format-json
*.json
# Already being linted by mdl
*.md
# Already being linted by yamllint
 7  .yamllint 
@@ -0,0 +1,7 @@
---
extends: default

rules:
  # yamllint doesn't like when we use yes and no for true and false,
  # but that's pretty standard in Ansible.
  truthy: disable
  29  CONTRIBUTING.md 
@@ -8,8 +8,8 @@ of contribution, and don't want a wall of rules to get in the way of
that.

Before contributing, we encourage you to read our CONTRIBUTING policy
(you are here), our [LICENSE](LICENSE.md), and our
[README](README.md), all of which should be in this repository.
(you are here), our [LICENSE](LICENSE), and our [README](README.md),
all of which should be in this repository.

## Issues ##

@@ -26,11 +26,11 @@ one.

If you choose to [submit a pull
request](https://github.com/cisagov/assessment-data-import-lambda/pulls),
you will notice that our continuous integration (CI) system runs a fairly
extensive set of linters and syntax checkers.  Your pull request may
fail these checks, and that's OK.  If you want you can stop there and
wait us to make the necessary corrections to ensure your code
passes the CI checks.
you will notice that our continuous integration (CI) system runs a
fairly extensive of linters, syntax checkers, system, and unit tests.
Your pull request may fail these checks, and that's OK.  If you want
you can stop there and wait for us to make the necessary corrections
to ensure your code passes the CI checks.

If you want to make the changes yourself, or if you want to become a
regular contributor, then you will want to set up
@@ -77,7 +77,7 @@ Once `pyenv` and `pyenv-virtualenv` are installed on your system, you
can create and configure the Python virtual environment with these
commands:

```bash
```console
cd assessment-data-import-lambda
pyenv virtualenv <python_version_to_use> assessment-data-import-lambda
pyenv local assessment-data-import-lambda
@@ -88,14 +88,25 @@ pip install -r requirements-dev.txt

Now setting up pre-commit is as simple as:

```bash
```console
pre-commit install
```

At this point the pre-commit checks will run against any files that
you attempt to commit.  If you want to run the checks against the
entire repo, just execute `pre-commit run --all-files`.

### Running unit and system tests ###

In addition to the pre-commit checks the CI system will run the suite
of unit and system tests that are included with this project.  To run
these tests locally execute `pytest` from the root of the project.

We encourage any updates to these tests to improve the overall code
coverage.  If your pull request adds new functionality we would
appreciate it if you extend existing test cases, or add new ones to
exercise the newly added code.

## Public domain ##

This project is in the public domain within the United States, and
 0  LICENSE.md → LICENSE 
File renamed without changes.
  6  README.md 
@@ -1,8 +1,10 @@
# assessment-data-import-lambda ƛ #

[![Build Status](https://travis-ci.com/cisagov/assessment-data-import-lambda.svg?branch=develop)](https://travis-ci.com/cisagov/assessment-data-import-lambda)
[![GitHub Build Status](https://github.com/cisagov/assessment-data-import-lambda/workflows/build/badge.svg)](https://github.com/cisagov/assessment-data-import-lambda/actions)
[![Coverage Status](https://coveralls.io/repos/github/cisagov/assessment-data-import-lambda/badge.svg?branch=develop)](https://coveralls.io/github/cisagov/assessment-data-import-lambda?branch=develop)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/cisagov/assessment-data-import-lambda.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/assessment-data-import-lambda/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/cisagov/assessment-data-import-lambda.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/assessment-data-import-lambda/context:python)
[![Known Vulnerabilities](https://snyk.io/test/github/cisagov/assessment-data-import-lambda/develop/badge.svg)](https://snyk.io/test/github/cisagov/assessment-data-import-lambda)

`assessment-data-import-lambda` contains code to build an AWS Lambda function
that reads assessment data from a JSON file in an S3 bucket and imports it
@@ -27,7 +29,7 @@ using this tool.

## License ##

This project is in the worldwide [public domain](LICENSE.md).
This project is in the worldwide [public domain](LICENSE).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
 4  adi/__init__.py 
@@ -1,3 +1,5 @@
"""This package contains the assessment_data_import code."""
from .assessment_data_import import import_data
from ._version import __version__  # noqa: F401

__version__ = "1.0.0"
__all__ = ["import_data"]
 2  adi/_version.py 
@@ -0,0 +1,2 @@
"""This file defines the version of this module."""
__version__ = "1.0.0"
  5  adi/assessment_data_import.py 
@@ -39,6 +39,7 @@
import json
import logging
import os
import sys
import tempfile

# Third-party libraries (install with pip)
@@ -48,7 +49,7 @@
from pytz import utc

# Local library
from adi import __version__
from ._version import __version__


def import_data(
@@ -274,4 +275,4 @@ def main():


if __name__ == "__main__":
    main()
    sys.exit(main())
 2  pytest.ini 
@@ -0,0 +1,2 @@
[pytest]
addopts = -v -ra --cov
  21  setup.py 
@@ -5,21 +5,33 @@
- https://packaging.python.org/distributing/
- https://github.com/pypa/sampleproject/blob/master/setup.py
- https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
"""

from glob import glob
from os.path import splitext, basename

from setuptools import setup


def readme():
    """Read in and return the contents of the project's README.md file."""
    with open("README.md") as f:
    with open("README.md", encoding="utf-8") as f:
        return f.read()


def package_vars(version_file):
    """Read and return the variables defined by the version_file."""
    pkg_vars = {}
    with open(version_file) as f:
        exec(f.read(), pkg_vars)  # nosec
    return pkg_vars


setup(
    name="adi",
    # Versions should comply with PEP440
    version="1.0.0",
    version=package_vars("adi/_version.py")["__version__"],
    description="Imports assessment data to a Mongo database",
    long_description=readme(),
    long_description_content_type="text/markdown",
@@ -51,8 +63,9 @@ def readme():
    # What does your project relate to?
    keywords="adi assessment import",
    packages=["adi"],
    install_requires=["docopt"],
    extras_require={"test": ["pre-commit"]},
    py_modules=[splitext(basename(path))[0] for path in glob("adi/*.py")],
    install_requires=["docopt", "setuptools"],
    extras_require={"test": ["pre-commit", "pytest", "pytest-cov", "coveralls"]},
    # Conveniently allows one to run the CLI tool as `example`
    entry_points={"console_scripts": ["adi = adi.assessment_data_import:main"]},
)
 0  tag.sh  100644 → 100755
Empty file.
 28  tests/conftest.py 
@@ -0,0 +1,28 @@
"""pytest plugin configuration.
https://docs.pytest.org/en/latest/writing_plugins.html#conftest-py-plugins
"""
import pytest


def pytest_addoption(parser):
    """Add new commandline options to pytest."""
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    """Register new markers."""
    config.addinivalue_line("markers", "slow: mark test as slow")


def pytest_collection_modifyitems(config, items):
    """Modify collected tests based on custom marks and commandline options."""
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
