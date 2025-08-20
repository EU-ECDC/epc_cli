import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import sys
import logging
import os
import json
import certifi

def load_config(json_config):
    config = None
    # reading the configuration file
    if os.path.isfile(json_config):
        with open(json_config, 'r') as j:
            config = json.load(j)
        return(config)
    else:
        raise Exception(f"{json_config} not found")

def request_token(config_data):
    logging.info("Requesting token")
    token = ""
    request_payload = {
        "grant_type": "password",
        "client_id": config_data["credentials"]["client_id"],
        "client_secret": config_data["credentials"]["client_secret"],
        "username": config_data["credentials"]["username"],
        "password": config_data["credentials"]["password"],
        "resource": config_data["env"]["resource"],
        "scope": "openid"
    }
    response = requests.post(config_data["env"]["authentication_url"], data = request_payload, verify = certifi.where())
    if response.status_code == 200:
        try:
            token = response.json().get("access_token")
        except:
            print(f"{response.status_code} | {response.text}")
            print("ERROR: I was not able to parse the response")
    else:
        print(f"{response.status_code} | {response.text}")
    if token == "":
        sys.exit()
    else:
        print("    token: {}[...]".format(token[:10]))        
        return token
