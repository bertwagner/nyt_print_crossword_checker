import base64
import hmac
import hashlib
import datetime
import boto3
import json

# Amazon v4 Signature calc documentation/examples: 
# https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html#signing-request-intro
# https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-post-example.html

ACCESS_KEY='AKIA3ALIEMYGXF3P5TPZ'

def base64_upload_policy(expiration,amzdate,datestamp):
    policy = '''{ "expiration": "'''+expiration+'''",
                    "conditions": [
                        {"bucket": "crosschecker.app-data"},
                        ["starts-with", "$key", "image_uploads/"],
                        {"acl": "private"},
                        {"x-amz-credential": "'''+ACCESS_KEY+'''/'''+datestamp+'''/us-east-1/s3/aws4_request"},
                        {"x-amz-algorithm": "AWS4-HMAC-SHA256"},
                        {"x-amz-date": "'''+amzdate+'''" }
                    ]
                }'''

    # Convert to CRLF and then base64
    policy = policy.replace('\n', '\r\n').encode('utf-8')
    base64_bytes = base64.b64encode(policy)

    return base64_bytes

def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def get_signature_key(key, dateStamp, regionName, serviceName):
    kDate = sign(("AWS4" + key).encode("utf-8"), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, "aws4_request")
    return kSigning

def get_secret():
    client = boto3.client('secretsmanager')

    response = client.get_secret_value(
        SecretId='crosschecker-image-uploader-user-access-key'
    )
    secret = json.loads(response["SecretString"])[ACCESS_KEY]

    return secret

def lambda_handler(event, context):
    t = datetime.datetime.utcnow()
    amzdate = t.strftime('%Y%m%dT%H%M%SZ') #"20211129T000000Z"
    datestamp = t.strftime('%Y%m%d') #"20211129"
    expiration_datestamp = (t + datetime.timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ') #"2021-12-29T12:00:00.000Z" #

    string_to_sign = base64_upload_policy(expiration_datestamp,amzdate,datestamp).decode('utf-8')

    secret = get_secret()
    signing_key = get_signature_key(secret,datestamp,"us-east-1","s3")

    signature = sign(signing_key,string_to_sign).hex()

    message = 'Hello {} {}!'.format(event['first_name'], event['last_name'])  
    return { 
        'message' : message
    }


lambda_handler(None,None)