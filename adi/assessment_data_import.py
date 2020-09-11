#!/usr/bin/env python3

"""adi: A tool for importing assessment data.

The source assessment data is a JSON file stored in an AWS S3 bucket.
The destination of the data is a Mongo database.

Usage:
  adi --s3-bucket=BUCKET --data-filename=FILE --db-hostname=HOST [--db-port=PORT] --ssm-db-name=DB --ssm-db-user=USER --ssm-db-password=PASSWORD [--log-level=LEVEL]
  adi (-h | --help)

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

# Standard Python Libraries
import datetime
import json
import logging
import os
import sys
import tempfile

# Third-Party Libraries
from boto3 import client as boto3_client
import docopt
from pymongo import MongoClient
from pytz import utc

# Local library
from ._version import __version__


def import_data(
    s3_bucket=None,
    data_filename=None,
    db_hostname=None,
    db_port="27017",
    ssm_db_name=None,
    ssm_db_user=None,
    ssm_db_password=None,
    log_level="warning",
):
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
    bool : Returns a boolean indicating if the assessment data import was
    successful.

    """
    # Boto3 clients for S3 and SSM
    s3_client = boto3_client("s3")
    ssm_client = boto3_client("ssm")

    # Securely create a temporary file to store the JSON data in
    temp_file_descriptor, temp_assessment_filepath = tempfile.mkstemp()

    try:
        # Fetch assessment data file from S3 bucket
        s3_client.download_file(
            Bucket=s3_bucket, Key=data_filename, Filename=temp_assessment_filepath
        )
        logging.info("Retrieved %s from S3 bucket %s", data_filename, s3_bucket)

        # Load assessment data JSON
        with open(temp_assessment_filepath) as assessment_json_file:
            assessment_data = json.load(assessment_json_file)
        logging.info("JSON data loaded from %s", data_filename)

        # Fetch database credentials from AWS SSM
        db_info = dict()
        for ssm_param_name, key in (
            (ssm_db_name, "db_name"),
            (ssm_db_user, "username"),
            (ssm_db_password, "password"),
        ):
            response = ssm_client.get_parameter(
                Name=ssm_param_name, WithDecryption=True
            )
            db_info[key] = response["Parameter"]["Value"]

        # Set up database connection
        db_uri = (
            f"mongodb://{db_info['username']}:{db_info['password']}@"
            f"{db_hostname}:{db_port}/{db_info['db_name']}"
        )

        db_connection = MongoClient(host=db_uri, tz_aware=True)
        db = db_connection[db_info["db_name"]]
        logging.info(
            "DB connection set up to %s:%d/%s", db_hostname, db_port, db_info["db_name"]
        )

        # Iterate through assessment data and save each record to the database
        for index, assessment in enumerate(assessment_data):
            # Check for the most required of fields
            if "id" not in assessment:
                logging.warning(
                    "Assessment at index %d missing 'id'! Skipping...", index
                )
                continue

            # Ensure other required fields are present
            missing_fields = [
                k
                for k in (
                    "Asmt Name",
                    "Assessment Type",
                    "created",
                    "Stakeholder Name",
                    "status",
                )
                if k not in assessment
            ]
            if missing_fields:
                logging.warning(
                    "'%s' is missing the following required field(s):", assessment["id"]
                )
                for field in missing_fields:
                    logging.warning("Missing field '%s'", field)
                logging.warning("Skipping...")
                continue

            # Convert dates to UTC datetimes
            for date_field in (
                "Appendix A Date",
                "created",
                "Draft Complete Date",
                "External Testing Begin Date",
                "External Testing End Date",
                "resolved",
                "Internal Testing Begin Date",
                "Internal Testing End Date",
                "Report Final Date",
                "ROE Date",
                "Testing Begin Date",
                "Testing Complete Date",
                "updated",
            ):
                if assessment.get(date_field):
                    assessment[date_field] = datetime.datetime.strptime(
                        assessment[date_field], "%a, %d %b %Y %H:%M:%S %z"
                    )
                    assessment[date_field] = (
                        assessment[date_field].replace(tzinfo=utc)
                        - assessment[date_field].utcoffset()
                    )

            db.assessments.replace_one(
                {"_id": assessment["id"]},
                {
                    # Required fields
                    "_id": assessment["id"],
                    "assessment_name": assessment["Asmt Name"],
                    "assessment_status": assessment["status"],
                    "assessment_type": assessment["Assessment Type"],
                    "created": assessment["created"],
                    "stakeholder_name": assessment["Stakeholder Name"],
                    # Optional fields
                    "appendix_a_signed": assessment.get("Appendix A Signed"),
                    "appendix_a_signed_date": assessment.get("Appendix A Date"),
                    "appendix_b_signed": assessment.get("Appendix B Signed"),
                    "assessment_completed": assessment.get("resolved"),
                    "assessment_summary": assessment.get("summary"),
                    "ci_systems": assessment.get("CI Systems"),
                    "ci_type": assessment.get("CI Type"),
                    "contractor_count": assessment.get("Contractor Operator Count"),
                    "draft_completed": assessment.get("Draft Complete Date"),
                    "election": assessment.get("Election"),
                    "external_testing_begin": assessment.get(
                        "External Testing Begin Date"
                    ),
                    "external_testing_end": assessment.get("External Testing End Date"),
                    "fed_count": assessment.get("Fed Operator Count"),
                    "fed_lead": assessment.get("Fed Lead"),
                    "group_project": assessment.get("Group/Project"),
                    "internal_testing_begin": assessment.get(
                        "Internal Testing Begin Date"
                    ),
                    "internal_testing_city": assessment.get("Internal Testing City"),
                    "internal_testing_end": assessment.get("Internal Testing End Date"),
                    "last_change": assessment.get("updated"),
                    "management_request": assessment.get("Mgmt Req"),
                    "mandated_category": assessment.get("Mandated Category"),
                    "operators": assessment.get("Operators", []),
                    "report_final_date": assessment.get("Report Final Date"),
                    "requested_services": assessment.get("Requested Services", []),
                    "roe_number": assessment.get("ROE Number"),
                    "roe_signed": assessment.get("ROE Signed"),
                    "roe_signed_date": assessment.get("ROE Date"),
                    "sector": assessment.get("Testing Sector"),
                    "stakeholder_state": assessment.get("State"),
                    "testing_begin": assessment.get("Testing Begin Date"),
                    "testing_complete": assessment.get("Testing Complete Date"),
                    "testing_phase": assessment.get("Testing Phase", []),
                },
                upsert=True,
            )
        logging.info(
            "%d assessment documents successfully inserted/updated in database",
            len(assessment_data),
        )

        # Delete assessment data object from S3 bucket
        s3_client.delete_object(Bucket=s3_bucket, Key=data_filename)
        logging.info("Deleted %s from S3 bucket %s", data_filename, s3_bucket)
    finally:
        # Delete local temp assessment data file regardless of whether or not
        # any exceptions were thrown in the try block above
        os.remove(temp_assessment_filepath)
        logging.info("Deleted temporary %s from local filesystem", data_filename)

    return True


def main():
    """Set up logging and call the import_data function."""
    # Parse command line arguments
    args = docopt.docopt(__doc__, version=__version__)

    # Set up logging
    log_level = args["--log-level"]
    try:
        logging.basicConfig(
            format="%(asctime)-15s %(levelname)s %(message)s", level=log_level.upper()
        )
    except ValueError:
        logging.critical(
            "'%s' is not a valid logging level. Possible values are debug, "
            + "info, warning, error, and critical.",
            log_level,
        )
        return 1

    result = import_data(
        args["--s3-bucket"],
        args["--data-filename"],
        args["--db-hostname"],
        args["--db-port"],
        args["--ssm-db-name"],
        args["--ssm-db-user"],
        args["--ssm-db-password"],
        args["--log-level"],
    )

    # Stop logging and clean up
    logging.shutdown()

    return result


if __name__ == "__main__":
    sys.exit(main())
