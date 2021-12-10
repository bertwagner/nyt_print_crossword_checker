import boto3
from botocore.errorfactory import ClientError
import json
import cv2
import numpy as np
import os
from io import BytesIO

SESSION = boto3.Session()
S3 = SESSION.client('s3')

def get_s3_image(bucket_name,key):
    s3_object = S3.get_object(Bucket=bucket_name, Key=key)
    body = s3_object['Body']
    nparr = np.fromstring(body.read(), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR) 
    return image

def check_crossword_answer_key(date):
    # check if answer key is cached
    try:
        S3.head_object(Bucket='crosschecker.app-data', Key=f'nyt_answer_keys/{date}.json')
    except ClientError:
        download_crossword_answer_key(date)

def get_secret():
    client = boto3.client('secretsmanager')

    response = client.get_secret_value(
        SecretId='crosschecker-nyt-login'
    )
    json_response = json.loads(response["SecretString"])

    return json_response['email'],json_response['password']

def download_crossword_answer_key(date):
    email,password = get_secret()
    

def process_image(image):
    return image



def lambda_handler(event, context):
    # TODO: figure out how this image name gets passed in when s3 triggers a lambda
    filename = "2021-12-07-bc998d20-77ff-4af7-ae0c-b152d464356c.png"

    # parse date out from image name
    date = filename[0:10]

    # ensure nyt crossword for this date is cached
    check_crossword_answer_key(date)

    # load the image
    image = get_s3_image("crosschecker.app-data",f"image_uploads/{filename}")

    # process the crossword image into individual squares

    

   

    return {
        "statusCode": 200,
        'headers': { 'Content-Type': 'application/json' },
        "body": {}
    }


lambda_handler(None,None)