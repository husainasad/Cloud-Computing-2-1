import boto3, json

with open('config.json') as f:
    config = json.load(f)

S3_Names = [config["INPUT_BUCKET"], config["STAGE1_BUCKET"]]
BUCKET_REGION = config["AWS_REGION"]

session = boto3.Session()
s3_client = session.client('s3', region_name=BUCKET_REGION)

for name in S3_Names:
    response = s3_client.create_bucket(Bucket = name)
    print(response)