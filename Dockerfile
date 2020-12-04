# Get the Python version to use from the commandline if provided
ARG PY_VERSION=3.8

FROM lambci/lambda:build-python$PY_VERSION

# Declare it a second time so it's brought into this scope.
ARG PY_VERSION=3.8
# Get the output file name base from the commandline if provided
ARG FILE_NAME=assessment-data-import

# For a list of pre-defined annotation keys and value types see:
# https://github.com/opencontainers/image-spec/blob/master/annotations.md
# Note: Additional labels are added by the build workflow.
LABEL org.opencontainers.image.authors="david.redmin@trio.dhs.gov"
LABEL org.opencontainers.image.vendor="Cyber and Infrastructure Security Agency"

# Bring the command line ARGs into the ENV so they are available in the
# generated image.
ENV BUILD_PY_VERSION=$PY_VERSION
ENV BUILD_FILE_NAME=$FILE_NAME

COPY build.sh .

COPY lambda_handler.py .

# Files needed to install local eal module
COPY README.md .
COPY requirements.txt .
COPY setup.py .
COPY adi ./adi

ENTRYPOINT ["./build.sh"]
