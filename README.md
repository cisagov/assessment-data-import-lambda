# assessment-data-import-lambda ƛ #

<<<<<<< HEAD
[![GitHub Build Status](https://github.com/cisagov/assessment-data-import-lambda/workflows/build/badge.svg)](https://github.com/cisagov/assessment-data-import-lambda/actions)
[![Coverage Status](https://coveralls.io/repos/github/cisagov/assessment-data-import-lambda/badge.svg?branch=develop)](https://coveralls.io/github/cisagov/assessment-data-import-lambda?branch=develop)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/cisagov/assessment-data-import-lambda.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/assessment-data-import-lambda/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/cisagov/assessment-data-import-lambda.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/assessment-data-import-lambda/context:python)
[![Known Vulnerabilities](https://snyk.io/test/github/cisagov/assessment-data-import-lambda/develop/badge.svg)](https://snyk.io/test/github/cisagov/assessment-data-import-lambda)
=======
## ⚠ Notice ⚠ ##

This project has been deprecated. A replacement project using a more modern
approach can be found at [cisagov/skeleton-aws-lambda-python](https://github.com/cisagov/skeleton-aws-lambda-python).
If you need to create AWS Lambdas using Python runtimes please base your project
on that skeleton.

[![GitHub Build Status](https://github.com/cisagov/skeleton-aws-lambda/workflows/build/badge.svg)](https://github.com/cisagov/skeleton-aws-lambda/actions)
[![Coverage Status](https://coveralls.io/repos/github/cisagov/skeleton-aws-lambda/badge.svg?branch=develop)](https://coveralls.io/github/cisagov/skeleton-aws-lambda?branch=develop)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/cisagov/skeleton-aws-lambda.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/skeleton-aws-lambda/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/cisagov/skeleton-aws-lambda.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/skeleton-aws-lambda/context:python)
[![Known Vulnerabilities](https://snyk.io/test/github/cisagov/skeleton-aws-lambda/develop/badge.svg)](https://snyk.io/test/github/cisagov/skeleton-aws-lambda)
>>>>>>> d2561c411f66c6477d7a3932860d98bc519b31e8

`assessment-data-import-lambda` contains code to build an AWS Lambda function
that reads assessment data from a JSON file in an S3 bucket and imports it
into a database.

## Building the AWS Lambda zip file ##

### Via a GitHub Release ###

This repository is configured with a
[GitHub Actions](https://github.com/features/actions) release workflow that
will automatically generate the Lambda zip file whenever a new release is
created.  The `assessment-data-import.zip` file can be found in the list of
assets attached to each
[release](https://github.com/cisagov/assessment-data-import-lambda/releases).

### Manually ###

1. `cd ~/cisagov/assessment-data-import-lambda`
1. `docker-compose down`
1. `docker-compose build`
1. `docker-compose up`

## Note ##

Please note that the corresponding Docker image _must_ be rebuilt
locally if the script `build.sh` changes.  Given that rebuilding the Docker
image is very fast (due to Docker's caching) if the script has not changed, it
is a very good idea to _always_ run the `docker-compose build` step when
using this tool.

## Contributing ##

We welcome contributions!  Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for
details.

## License ##

This project is in the worldwide [public domain](LICENSE).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
