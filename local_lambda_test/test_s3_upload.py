import boto3
import os
from moto import mock_aws

BUCKET_NAME = "mock-bucket"
FILENAME = "Sahiti_transactions.csv"

@mock_aws  # ← FIXED: Removed ("s3")
def test_upload():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=BUCKET_NAME)

    # Create test file
    if not os.path.exists(FILENAME):
        with open(FILENAME, "w") as f:
            f.write("Date,Action,Amount,Balance\n")
            f.write("2025-06-21,Deposit,1000,5000\n")

    # Upload to mock bucket
    s3.upload_file(FILENAME, BUCKET_NAME, FILENAME)

    # Check contents
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    keys = [item["Key"] for item in response.get("Contents", [])]

    assert FILENAME in keys
    print("✅ Mock S3 upload successful!")

test_upload()
