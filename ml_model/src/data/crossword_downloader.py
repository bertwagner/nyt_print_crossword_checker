import cv2
import numpy as np
import boto3
from botocore.errorfactory import ClientError
import json
import requests
import re
import datetime

class CrosswordDownloader:
    BUCKETNAME='crosschecker.app-data'

    def __init__(self):
        self.session = boto3.Session()
        self.s3 = self.session.client('s3')

    def get_answer_key(self,date):

        answer_key = self._check_crossword_answer_key(date)
        return answer_key

    def _check_crossword_answer_key(self,date):
        # check if answer key is cached
        date_string = date.strftime("%Y-%m-%d")
        try:
            self.s3.head_object(Bucket=self.BUCKETNAME, Key=f'nyt_answer_keys/{date_string}.json')
        except ClientError:
            self._download_crossword_answer_key(date)
        
        # get the answer key form s3
        s3_object = self.s3.get_object(Bucket=self.BUCKETNAME, Key=f'nyt_answer_keys/{date}.json')
        raw_json_answer_key = json.loads(s3_object['Body'].read().decode('utf-8'))

        processed_answer_key = self._process_answer_key(raw_json_answer_key)

        return processed_answer_key

    def _get_secret(self):
        client = boto3.client('secretsmanager')

        response = client.get_secret_value(
            SecretId='crosschecker-nyt-login'
        )
        json_response = json.loads(response["SecretString"])

        return json_response['email'],json_response['password']

    def _download_crossword_answer_key(self,date):
        email,password = self._get_secret()
        
        s = requests.Session()

        # GET the auth token from the login page
        url = 'https://myaccount.nytimes.com/auth/enter-email?response_type=cookie&client_id=lgcl&redirect_uri=https%3A%2F%2Fwww.nytimes.com'
        r = s.get(url)
        m = re.search('(?<=authToken&quot;:&quot;).*?(?=&quot;)', r.text)
        auth_token = m.group(0).replace("&#x3D;","=") #encode html entities
       
       # First page that asks for email address
        url = 'https://myaccount.nytimes.com/svc/lire_ui/authorize-email'
        data = '{"email":"%s","auth_token":"%s","form_view":"enterEmail"}' % (email, auth_token)
        r = s.post(url,json=json.loads(data))

        # Second page that asks for password
        url = "https://myaccount.nytimes.com/svc/lire_ui/login"

        payload="{\"username\":\"%s\",\"auth_token\":\"%s\",\"form_view\":\"login\",\"password\":\"%s\",\"remember_me\":\"Y\"}" % (email,auth_token,password)
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://myaccount.nytimes.com/auth/enter-email?response_type=cookie&client_id=lgcl&redirect_uri=https%3A%2F%2Fwww.nytimes.com',
        'Content-Type': 'application/json',
        'Req-Details': '[[it:lui]]',
        'Origin': 'https://myaccount.nytimes.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'TE': 'trailers'
        }

        r = s.request("POST", url, headers=headers, data=payload)
        
        # get the puzzle id
        date_string = date.strftime("%Y-%m-%d")
        url = 'https://nyt-games-prd.appspot.com/svc/crosswords/v3/36569100/puzzles.json?publish_type=daily&sort_order=asc&sort_by=print_date&date_start=%s&date_end=%s' % (date_string,date_string)
        r = s.post(url,json=json.loads(data))
        puzzle_id = r.json()['results'][0]['puzzle_id']

        # Download the json
        url = 'https://www.nytimes.com/svc/crosswords/v2/puzzle/%s.json' % puzzle_id
        r = s.get(url)

        self._save_answer_key_to_s3(r.content,date)

    def _save_answer_key_to_s3(self,json,date):
        filename = "%s.json" % date.strftime("%Y-%m-%d")
        self.s3.put_object(Body=json, Bucket='crosschecker.app-data', Key='nyt_answer_keys/%s' % filename)

    def _process_answer_key(self,json):
        return json["results"][0]["puzzle_data"]["answers"]

if __name__ == '__main__':
    cd = CrosswordDownloader()
    targets = cd.get_answer_key(datetime.date(2021,12,13))