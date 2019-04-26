import json
import logging
import os

from boto3 import client as boto3_client

# This Lambda function expects the following environment variables to be
# defined:
# 1. assessment_data_s3_bucket - The name of the bucket where the assessment
# data JSON file lives
# 2. assessment_data_filename - The name of the assessment data JSON file in
# the assessment_data_s3_bucket
# 3. db_creds_s3_bucket - The name of the bucket where the database credentials
# YAML file lives
# 4. db_creds_filename - The name of the database credentials YAML file in the
# db_creds_s3_bucket

# In the case of AWS Lambda, the root logger is used BEFORE our Lambda handler
# runs, and this creates a default handler that goes to the console.  Once
# logging has been configured, calling logging.basicConfig() has no effect.  We
# can get around this by removing any root handlers (if present) before calling
# logging.basicConfig().  This unconfigures logging and allows --debug to
# affect the logging level that appears in the CloudWatch logs.
#
# See
# https://stackoverflow.com/questions/1943747/python-logging-before-you-run-logging-basicconfig
# and
# https://stackoverflow.com/questions/37703609/using-python-logging-with-aws-lambda
# for more details.
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)

        # Set up logging
        log_level = logging.DEBUG  #TODO Change back to WARNING when done debugging
        logging.basicConfig(format='%(asctime)-15s %(levelname)s %(message)s',
                            level=log_level)

def handler(event, context):
    """
    Handler for all Lambda events
    """
    # Boto3 clients for S3 and Lambda
    s3_client = boto3_client('s3')
    lambda_client = boto3_client('lambda')

    logging.info('AWS Event was: {}'.format(event))

    # s3.download_file('assessment-data-daver', 'remote-assessment-data.json', '/tmp/remote-assessment-data.json')

    # # This is an SQS message relayed by the parent Lambda function.
    # #
    # # Extract some variables from the event dictionary.  See
    # # https://docs.aws.amazon.com/AmazonS3/latest/dev/notification-content-structure.html
    # # for details on the event structure corresponding to objects created
    # # in an S3 bucket.
    # receipt_handle = event['ReceiptHandle']
    # body = json.loads(event['Body'])
    # success = {}
    # for record in body['Records']:
    #     bucket = record['s3']['bucket']['name']
    #     key = record['s3']['object']['key']
    #
    #     # Process the DMARC aggregate reports
    #     returnVal = s3.do_it(SCHEMA, bucket, key,
    #                          DOMAINS, REPORTS,
    #                          os.environ['elasticsearch_url'],
    #                          os.environ['elasticsearch_index'],
    #                          os.environ['elasticsearch_region'],
    #                          TOKEN, DELETE)
    #     logging.debug('Response from do_it() is {}'.format(returnVal))
    #
    #     # Update the success dictionary
    #     success = {**success, **returnVal}
    #
    #     # If everything succeeded then delete the message from the queue
    #     if all(v for v in success.values()):
    #         logging.info('Deleting message from queue after '
    #                      'successful processing')
    #         sqs_client.delete_message(QueueUrl=os.environ['queue_url'],
    #                                   ReceiptHandle=receipt_handle)
