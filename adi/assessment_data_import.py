#!/usr/bin/env python3

"""assessment-data-import: A tool for importing assessment data.

The source assessment data is a JSON file stored in an AWS S3 bucket.
The destination of the data is a Mongo database.

Usage:
  assessment-data-import --s3-bucket=BUCKET --data-filename=FILE --db-hostname=HOST [--db-port=PORT] --ssm-db-name=DB --ssm-db-user=USER --ssm-db-password=PASSWORD [--log-level=LEVEL]
  assessment-data-import (-h | --help)

Options:
  -h --help                   Show this message.
  --s3-bucket=BUCKET          The AWS S3 bucket containing the assessment data
                              file.
  --data-filename=FILE        The name of the file containing the assessment
                              data in the S3 bucket above.
  --db-hostname=HOST          The hostname that has the database to store
                              the assessment data in.
  --db-port=PORT              The port that the database server is
                              listening on. [default: 27017]
  --ssm-db-name=DB            The name of the parameter in AWS SSM that holds
                              the name of the database to store the assessment
                              data in.
  --ssm-db-user=USER          The name of the parameter in AWS SSM that holds
                              the database username with write permission to
                              the assessment database.
  --ssm-db-password=PASSWORD  The name of the parameter in AWS SSM that holds
                              the database password for the user with write
                              permission to the assessment database.
  --log-level=LEVEL           If specified, then the log level will be set to
                              the specified value.  Valid values are "debug",
                              "info", "warning", "error", and "critical".
                              [default: warning]
"""

# Standard libraries
import datetime
import json
import logging
import os

# Third-party libraries (install with pip)
from boto3 import client as boto3_client
import docopt
from pymongo import MongoClient
from pytz import utc

# Local library
from adi import __version__

def import_data(s3_bucket=None, data_filename=None, db_hostname=None,
                db_port="27017", ssm_db_name=None, ssm_db_user=None,
                ssm_db_password=None, log_level="warning"):
    """Import assessment data from a JSON file in an S3 bucket to a database.

    Parameters
    ----------
    s3_bucket : str
        The AWS S3 bucket containing the assessment data file.

    data_filename : str
        The name of the file containing the assessment data in the S3 bucket
        above.

    db_hostname : str
        The hostname that has the database to store the assessment data in.

    db_port : str
        The port that the database server is listening on. [default: 27017]

    ssm_db_name : str
        The name of the parameter in AWS SSM that holds the name of the
        database to store the assessment data in.

    ssm_db_user : str
        The name of the parameter in AWS SSM that holds the database username
        with write permission to the assessment database.

    ssm_db_password : str
        The name of the parameter in AWS SSM that holds the database password
        for the user with write permission to the assessment database.

    log_level : str
        If specified, then the log level will be set to the specified value.
        Valid values are "debug", "info", "warning", "error", and "critical".
        [default: warning]

    Returns
    -------
    bool : Returns a boolean indicating if the asssessment data import was
    successful.

    """
    # Boto3 clients for S3 and SSM
    s3_client = boto3_client("s3")
    ssm_client = boto3_client("ssm")

    # TODO Add error checking?
    # TODO Determine which fields are required vs. optional

    # Fetch assessment data file from S3 bucket
    s3_client.download_file(Bucket=s3_bucket, Key=data_filename,
                            Filename=f"/tmp/{data_filename}")
    logging.info(f"Retrieved {data_filename} from S3 bucket {s3_bucket}")

    # Load assessment data JSON
    with open(f"/tmp/{data_filename}") as assessment_json_file:
        assessment_data = json.load(assessment_json_file)
    logging.info(f"JSON data loaded from {data_filename}")

    # Fetch database credentials from AWS SSM
    db_info = dict()
    for ssm_param_name, key in (
        (ssm_db_name, "db_name"),
        (ssm_db_user, "username"),
        (ssm_db_password, "password")
    ):
        response = ssm_client.get_parameter(Name=ssm_param_name,
                                            WithDecryption=True)
        db_info[key] = response["Parameter"]["Value"]

    # Set up database connection
    db_uri = f"mongodb://{db_info['username']}:{db_info['password']}@" \
        f"{db_hostname}:{db_port}/{db_info['db_name']}"

    db_connection = MongoClient(host=db_uri, tz_aware=True)
    db = db_connection[db_info["db_name"]]
    logging.info(f"DB connection set up to {db_hostname}:{db_port}/"
                 f"{db_info['db_name']}")

    # Iterate through assessment data and save each record to the database
    for assessment in assessment_data:
        # Convert dates to UTC datetimes
        for date_field in ("ROE Date",
                           "Testing Complete Date"):
            if assessment.get(date_field):
                assessment[date_field] = datetime.datetime.strptime(
                    assessment[date_field],
                    '%a, %d %b %Y %H:%M:%S %z')
                assessment[date_field] = assessment[date_field].replace(
                    tzinfo=utc) - assessment[date_field].utcoffset()

        db.rva.replace_one({"_id": assessment["id"]}, {
            "_id": assessment["id"],
            # "status": assessment.get("Status"),
            # "created": assessment.get("Created"),
            # "updated": assessment.get("Updated"),
            # "appendix_a_date": assessment.get("Appendix A Date"),
            "appendix_a_signed": assessment.get("Appendix A Signed"),
            "appendix_b_signed": assessment.get("Appendix B Signed"),
            "assessment_type": assessment.get("Assessment Type"),
            # "external_testing_begin_date": assessment.get("TBD"),
            # "external_testing_end_date": assessment.get("TBD"),
            # "group": assessment.get("TBD"),
            # "internal_testing_begin_date": assessment.get("TBD"),
            # "internal_testing_city": assessment.get("TBD"),
            # "internal_testing_end_date": assessment.get("TBD"),
            "mgmt_req": assessment.get("Mgmt Req"),
            "roe_date": assessment.get("ROE Date"),
            "roe_number": assessment.get("ROE Number"),
            "roe_signed": assessment.get("ROE Signed"),
            # "summary": assessment.get("Summary"),
            "asmt_name": assessment.get("Asmt Name"),
            # "requested_services": assessment.get("TBD"),
            "stakeholder_name": assessment.get("Stakeholder Name"),
            "state": assessment.get("State"),
            "testing_complete_date": assessment.get("Testing Complete Date"),
            # "testing_phase": assessment.get("TBD"),
            "election": assessment.get("Election"),  # TODO: Make real boolean
            "testing_sector": assessment.get("Testing Sector"),
            # "ci_type": assessment.get("TBD"),
            # "ci_systems": assessment.get("TBD"),
            "fed_lead": assessment.get("Fed Lead"),
            # "contractor_operator_count": assessment.get("TBD"),
            # "draft_poc_date": assessment.get("TBD"),
            # "fed_operator_count": assessment.get("TBD"),
            # "report_final_date": assessment.get("TBD"),
            # "operators": assessment.get("TBD"),
            # "stakeholder_id": assessment.get("TBD"),
            # "testing_begin_date": assessment.get("TBD")
        }, upsert=True)
    logging.info(f"{len(assessment_data)} assessment documents "
                 "successfully inserted/updated in database")

    # Delete local assessment data file from /tmp and from S3 bucket
    os.remove(f"/tmp/{data_filename}")
    s3_client.delete_object(Bucket=s3_bucket, Key=data_filename)
    logging.info(f"Deleted {data_filename} from local filesystem "
                 f"and from S3 bucket {s3_bucket}")

    return True


def main():
    # Parse command line arguments
    args = docopt.docopt(__doc__, version=__version__)

    # Set up logging
    log_level = args["--log-level"]
    try:
        logging.basicConfig(
            format="%(asctime)-15s %(levelname)s %(message)s",
            level=log_level.upper()
        )
    except ValueError:
        logging.critical(
            f'"{log_level}" is not a valid logging level.  Possible values '
            "are debug, info, warning, error, and critical."
        )
        return 1

    result = import_data(args["--s3-bucket"], args["--data-filename"],
                         args["--db-hostname"], args["--db-port"],
                         args["--ssm-db-name"], args["--ssm-db-user"],
                         args["--ssm-db-password"], args["--log-level"])

    # Stop logging and clean up
    logging.shutdown()

    return result


if __name__ == "__main__":
    main()
