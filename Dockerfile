FROM lambci/lambda:build-python3.6
MAINTAINER David Redmin <david.redmin@trio.dhs.gov>

COPY build.sh .
COPY adi ./adi
COPY lambda_handler.py .

ENTRYPOINT ["./build.sh"]
