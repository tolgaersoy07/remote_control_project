import boto3
import requirements
dynamodb=boto3.resource('dynamodb',
aws_access_key_id=requirements.aws_access_key_id,
aws_secret_access_key=requirements.aws_secret_access_key,
region_name=requirements.region_name)