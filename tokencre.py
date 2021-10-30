

import requests
from requests.auth import HTTPBasicAuth

import os
import json

from dotenv import load_dotenv

load_dotenv() 

 
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
redirect_uri = os.environ.get("REDIRECT_URI")
access_token = os.environ.get("TOKEN")


def create_access_token(client_id, client_secret, region = 'us'):
    url = "https://%s.battle.net/oauth/token" % region
    body = {"grant_type": 'client_credentials'}
    auth = HTTPBasicAuth(client_id, client_secret)

    response = requests.post(url, data=body, auth=auth)
    return response.json()





tokeni = create_access_token(client_id,client_secret,"eu")
print(tokeni)

def getBattleTag(BattleNetToken, region):
    url = f"https://{region}.battle.net/oauth/userinfo?access_token={BattleNetToken}"
    response = requests.get(url)
    return response.json()



print(getBattleTag(tokeni['access_token'] ,'eu'))
