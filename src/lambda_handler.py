import sys
import io
import os
import json
import urllib.parse
import boto3
import csv

print('Loading custom function')

# CONSTANTS
S3_CLIENT = boto3.client('s3')
SES_CLIENT = boto3.client('ses', region_name="us-east-2")

DYNAMODB_CLIENT = boto3.client("dynamodb")
DYNAMO_TABLE_NAME = "txn-processor-balance"

TO_EMAIL_ACCOUNT = os.getenv('TO_EMAIL_ACCOUNT')
FROM_EMAIL_ACCOUNT = os.getenv('FROM_EMAIL_ACCOUNT')
SES_CONFIG_SET_NAME = os.environ["SES_CONFIG_SET_NAME"]


def lambda_handler(event, context):
    # print("m=lambda_handler, Received event: " + json.dumps(event, indent=2))

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        # Get the s3 object
        response = S3_CLIENT.get_object(Bucket=bucket, Key=key)
        data = response['Body'].read().decode('utf-8')
        reader = csv.reader(io.StringIO(data))
        next(reader)

        average_credit_amount = 0
        average_debit_amount = 0
        total_balance = 0

        for row in reader:
            txn_id = row[0]
            txn_date = row[1]
            txn_amount = row[2]

            average_credit_amount += float(txn_amount) if float(txn_amount) > 0 else 0
            average_debit_amount += float(txn_amount) if float(txn_amount) < 0 else 0
            total_balance += float(txn_amount)
            print("m=lambda_handler" + str.format("id: {} date: {} transaction: {}", txn_id, txn_date, txn_amount))

            # Insert elements from CSV to DynamoDB
            insert_account_balance_txn(txn_id, txn_date, txn_amount)

        # Send account balance email
        print("m=lambda_handler, Sending email to: " + TO_EMAIL_ACCOUNT)
        send_account_balance_email(average_credit_amount, average_debit_amount, total_balance)

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e


def insert_account_balance_txn(txn_id: str, txn_date: str, txn_amount: str):
    txn_date_array = txn_date.split("/")

    response = DYNAMODB_CLIENT.put_item(
        TableName=DYNAMO_TABLE_NAME,
        Item={
            "id": {"S": txn_id},
            "day": {"S": txn_date_array[1]},
            "month": {"S": txn_date_array[0]},
            "transaction": {"N": txn_amount},
        },
    )
    # print(response)


def send_account_balance_email(average_credit_amount: float, average_debit_amount: float, total_balance: float):
    body_html = f"""
        <html>
        <head>
            <title>Stori: Tarjeta de cr&eacute;dito sin Bur&oacute;</title>
        </head>
        <body>
            <div style="background-color: #f6f8fb;">
            
                <div id="header">
                    <img src="https://finnovating.s3.eu-central-1.amazonaws.com/companies/company_26535/main_logo_26535.png" alt="Stori">
                </div>
            
                <div id="main">
                    <table style="padding: 15px; border-spacing: 10px;">
                        <tr>
                            <td colspan="3"><h1>Summary Account Balance</h1></td>
                        </tr>
                        <tr>
                            <td>
                                <p>Number of transactions in August: 2</p>
                                <p>Number of transactions in July: 2</p>
                            </td>
                            <td><br/></td>
                            <td>
                                <p>Average credit amount: {average_credit_amount:.2f}</p>
                                <p>Average debit amount: {average_debit_amount:.2f}</p>
                            </td>
                        </tr>
                        <tr>
                            <td colspan="3"><h2>Total balance is {total_balance:.2f}</h2></td>
                        </tr>
                    </table>
                </div>
        
                <div id="footer" style="background-color: white;">
                    <p>
                        Producto ofrecido por Mi Stori S.A. de C.V.
                    </p>
                    <p>
                        *L&iacute;nea de cr&eacute;dito en pesos mexicanos, aprobaci&oacute;n sujeta a evaluaci&oacute;n de la documentaci&oacute;n proporcionada por el solicitante.
                    </p>
                    <p>
                        Sujeto a aprobaci&oacute;n de cr&eacute;dito | Copyright 2022
                    </p>
                </div>
            </div>
            
        </body>
        </html>
        """

    email_message = {
        'Body': {
            'Html': {
                'Charset': 'utf-8',
                'Data': body_html,
            },
        },
        'Subject': {
            'Charset': 'utf-8',
            'Data': "Story Card: Summary Account Balance",
        },
    }

    ses_response = SES_CLIENT.send_email(
        Destination={
            'ToAddresses': [TO_EMAIL_ACCOUNT],
        },
        Message=email_message,
        Source=FROM_EMAIL_ACCOUNT
    )
    print(f"ses response id received: {ses_response['MessageId']}.")
