#!/usr/bin/env python

import json
import os
from datetime import datetime
from io import FileIO
import argparse
import requests
import sys
import certifi
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", type=str, default="config.json",
                    help="path to configuration file")
args = parser.parse_args()

config = None
# reading the configuration file
if os.path.isfile(args.config):
    with open(args.config, 'r') as j:
        config = json.load(j)
else:
    raise Exception(f"{args.config} not found")

def request_token(config_data):
    request_payload = {
        "grant_type": "password",
        "client_id": config_data["credentials"]["client_id"],
        "client_secret": config_data["credentials"]["client_secret"],
        "username": config_data["credentials"]["username"],
        "password": config_data["credentials"]["password"],
        "resource": config_data["credentials"]["resource"],
        "scope": "openid"
    }
    response = requests.post(config_data["env"]["authentication_url"], data=request_payload, verify=False)
    if response.status_code == 200:
        try:
            token = response.json().get("access_token")
            return token
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")


def get_all_wgs_subjects(token, config_data):
    headers = {
        'Authorization': "Bearer {}".format(token)
    }
    endpoint = config_data["env"]["base_url_endpoint"] + "/api/v1/DataUploadAPI/AllWGSSubjects"
    response = requests.get(endpoint, headers=headers, verify=False)
    if response.status_code == 200:
        try:
            wgs_subjects = response.json()
            return wgs_subjects
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")


t = request_token(config)
print(get_all_wgs_subjects(t, config))

