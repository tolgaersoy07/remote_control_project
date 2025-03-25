import boto3
import time

dynamodb = boto3.client('dynamodb',
                        aws_access_key_id='YOUR_AWS_ACCESS_KEY',
                        aws_secret_access_key='YOUR_AWS_SECRET_KEY',
                        region_name='YOUR_AWS_REGION')

def control_Tables(tName):
    try:
        response = dynamodb.describe_table(TableName=tName)
        print("The " + tName + " table already exists.")
        return 0
    except dynamodb.exceptions.ResourceNotFoundException:
        return 1

def create_Users():
    dynamodb.create_table(
        TableName='Users',
        KeySchema=[
            {
                'AttributeName': 'userID',
                'KeyType': 'HASH'
            }],
        AttributeDefinitions=[
            {
                'AttributeName': 'userID',
                'AttributeType': 'S'
            }],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5})

    # Tabloyu oluşturduktan sonra bir süre bekle
    time.sleep(10)
    dynamodb.put_item(
        TableName='Users',
        Item={
            'userID': {'S': "admin"},
            'cAddress': {'S': 'Your address'},
            'cName': {'S': 'Your company name'},
            'cNumber': {'S': 'Your companys tax number'},
            'eMail': {'S': "your email address"},
            'name': {'S': 'Name'},
            'password': {'S': 'password'},
            'pNumber': {'S': 'Your phone number'},
            'status': {'S': 'Kurumsal'},
            'surName': {'S': 'Surname'},
            'taxNumber': {'S': 'Tax number'},
            'tcNumber': {'S': 'Tc Number'},
            'userAddress': {'S': 'Your address'},
            'userParent': {'S': 'creator_tolgaersoy'},
            'userType': {'S': '1'}
        })
    return 1

def create_DataTable():
    dynamodb.create_table(
        TableName='DataTable',
        KeySchema=[
            {
                'AttributeName': 'uniqueID',
                'KeyType': 'HASH'
            }],
        AttributeDefinitions=[
            {
                'AttributeName': 'uniqueID',
                'AttributeType': 'S'
            }],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5})
    print("DataTable table has been created.")
    # Tabloyu oluşturduktan sonra bir süre bekle
    time.sleep(10)
    dynamodb.put_item(
        TableName='DataTable',
        Item={
            'uniqueID': {'S': '0'},
            'data': {'S': '{}'},
            'dName': {'S': "TEST DEVICE. DON'T DELETE!"},
            'dpin': {'S': '{}'},
            'dtype': {'S': '{}'},
            'explain': {'S': '{}'},
            'gdata': {'S': '{}'},
            'gexplain': {'S': '{}'},
            'gpin': {'S': '{}'},
            'gtype': {'S': '{}'},
            'userID': {'S': 'admin'}
        })
    print("Test device has been created.")
    return 1

def main():
    if control_Tables("Users"):
        create_Users()
    if control_Tables("DataTable"):
        create_DataTable()
    print("Everything is completed.")
    return 1

#main()
