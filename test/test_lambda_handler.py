import json
import unittest
import boto3
from moto import mock_s3

S3_BUCKET_NAME = 'txn-processor-bucket'
DEFAULT_REGION = 'us-east-1'
S3_TEST_FILE_KEY = 'txns.csv'
S3_TEST_FILE_CONTENT = [
    ["id", "date", "transaction"],
    [0, "7/15", "+60.5"],
    [1, "7/28", "-10.3"],
    [2, "8/2", "-20.46"],
    [3, "8/13", "+10"]
]


@mock_s3
class TestLambdaFunction(unittest.TestCase):
    def setUp(self):
        self.s3 = boto3.resource('s3', region_name=DEFAULT_REGION)
        self.s3_bucket = self.s3.create_bucket(Bucket=S3_BUCKET_NAME)
        self.s3_bucket.put_object(Key=S3_TEST_FILE_KEY, Body=json.dumps(S3_TEST_FILE_CONTENT))

    def test_handler(self):
        from lambda_handler import handler
        event = {
            'Records': [
                {
                    's3': {
                        'bucket': {
                            'name': S3_BUCKET_NAME
                        },
                        'object': {
                            'key': S3_TEST_FILE_KEY
                        }
                    }
                }
            ]
        }
        result = handler(event, {})
        self.assertEqual(result, {'StatusCode': 200, 'Message': 'SUCCESS'})
