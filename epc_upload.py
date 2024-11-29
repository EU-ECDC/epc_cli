#!/usr/bin/env python

import json
import os
from datetime import datetime
from io import FileIO

import requests
import sys


def get_token(url):

    headers = {
                        'Accept': 'application/x-www-form-urlencoded',
                        'Content-Type': 'application/x-www-form-urlencoded'
                        # 'Authorization': f'Bearer {token}'
                    }

    # UAT
    # payload = {"grant_type": "password",
    #                      "client_id": "f142116f-a5d0-4089-bfaf-46bb0e5dd340",
    #                      "client_secret": "a0P5pZqkIJKORIqoLzwoYr_PJDZdpv86nA7k_48u",
    #                      "username": r"ecdcdmz\EPC_NL_GENERAL-U",
    #                      "password": "P@ssw0rd",
    #                      "resource": "https://survportaluat.ecdc.europa.eu/api/epipulsecases/dataupload",
    #                      "scope": "openid"}

    # DEV
    payload = {"grant_type": "password",
               "client_id": "facb0ef9-fde8-4277-8690-bf22f15f8fe5",
               "client_secret": "3dn2LwCt_Y6ztni9MRlF32s9xX56EprjO5Ah7Wq_",
               "username": r"zdev\EPC_NL_GENERAL-U",
               "password": "P@ssw0rd",
               "resource": r"https://epipulsedev.ecdc.azure/api/epipulsecases/dataupload",
               "scope": "openid"}

    response = requests.post(url, data=payload, headers=headers, verify=False)

    if response.status_code in [200, 202]:
        print(f"status code: {response.status_code}")
        print(f"text: SUCCESS")
        print(f"text: {response.text}")

    else:
        print(f"status code: {response.status_code}")
        print(f"text: {response.text}")
        sys.exit(1)

    return json.loads(response.text).get('access_token')


def get_user_permissions(url, token):
    headers = {
        # 'Accept': 'application/x-www-form-urlencoded',
        # 'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers, verify=False)

    if response.status_code in [200, 202]:
        print(f"status code: {response.status_code}")
        print(f"text: SUCCESS")
        print(f"text: {response.text}")

    else:
        print(f"status code: {response.status_code}")
        print(f"text: {response.text}")
        sys.exit(1)

    return response.text


def get_health(url):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        # 'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers, verify=False)

    if response.status_code in [200, 202]:
        print(f"status code: {response.status_code}")
        print(f"text: SUCCESS")
        print(f"text: {response.text}")

    else:
        print(f"status code: {response.status_code}")
        print(f"text: {response.text}")
        sys.exit(1)

    return json.loads(response.text)


def upload_file(url, token, file_path):
    # Calculate byte_array and stream file data
    with open(file_path, "rb") as file:
        data = file.read()
        byte_array = len(data)
    file_name = os.path.basename(file_path)
    x_file_id = f"{file_name.replace('.', '')}-{byte_array}-{datetime.now().isoformat().split('T')[0].replace('-', '')}"
    print(x_file_id)

    headers = {
        'Accept': 'multipart/form-data',
        'Content-Type': 'multipart/form-data',
        'Authorization': f'Bearer {token}',
        'X-File-Identifier': x_file_id
    }

    payload = {
                "start": '2024-10-01',
                "end": '2024-10-01',
                "ignoreDateStartEnd": False,
                "uploadType": 'Add/Update',
        "uploadFile": {
            "value": data,
        "options": {
            "filename": file_path,
            "contentType": None
        }
    }
}

    response = requests.post(url, headers=headers, data=payload, verify=False)

    if response.status_code in [200, 202]:
        print(f"status code: {response.status_code}")
        print(f"text: SUCCESS")
        print(f"text: {response.text}")

    else:
        print(f"status code: {response.status_code}")
        print(f"text: {response.text}")
        sys.exit(1)

    return response.text


if __name__ == "__main__":
    # UAT
    # token_url = 'https://zfs.ecdc.europa.eu/adfs/oauth2/token'
    # base_url = r'https://survportaluat.ecdc.europa.eu'

    # DEV
    token_url = "https://zfs.ecdc.azure/adfs/oauth2/token"
    base_url = r'https://epipulsedev.ecdc.azure'


    token = get_token(token_url)
    health = get_health(base_url + r'/Health')

    # user_permission = get_user_permissions(base_url + r'/api/v1/DataUploadAPI/UserPermissions', token)


    upload_file = upload_file(base_url + r'/api/v1/DataUploadAPI/Uploads', token, r'./PERT_NL_NEW_UPDATE.csv')

