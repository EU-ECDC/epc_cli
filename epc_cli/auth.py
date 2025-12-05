import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import sys
import logging
import os
import json
import certifi
import keyring
from keyrings.cryptfile.cryptfile import CryptFileKeyring
import time
import getpass


def load_config(json_config):
    config = None
    # reading the configuration file
    if os.path.isfile(json_config):
        with open(json_config, 'r') as j:
            config = json.load(j)
        return(config)
    else:
        raise Exception(f"{json_config} not found")


def set_cryptfile_keyring(kr_path = None):
    logging.info("Accesing the keyring")
    kr = CryptFileKeyring()
    if kr_path:
        kr.file_path = kr_path
    logging.debug(f"Keyring path: {kr.file_path}\n")
    m_psswd = getpass.getpass(f"Please enter the master password of the keyring: ")
    kr.keyring_key = m_psswd
    keyring.set_keyring(kr)
    logging.debug(f"Keyring unlocked\n")

def is_token_potentially_valid(config_data):
    TOKEN_MAX_AGE = 3000  # seconds 
    token_potentially_valid = False
    if not os.path.isfile(f"{config_data['application_data']}/token.json"):
        logging.debug(f"{config_data['application_data']}/token.json does not exist")
        return(False)
    now = time.time()
    mtime = os.path.getmtime(f"{config_data['application_data']}/token.json")
    if now - mtime < TOKEN_MAX_AGE:
        token_potentially_valid = True         
    return(token_potentially_valid)


def read_token(config_data):
    token = None
    token_file = f"{config_data['application_data']}/token.json"
    with open(token_file, "r") as f:
        try:
            data_p = json.load(f)
            return(data_p.get("epc_token"))
        except json.JSONDecodeError:
            logging.error("Could not decode JSON in the token file.")
        except FileNotFoundError:
            logging.warning(f"Token file not found: {config_data['application_data']}/token.json")
        except Exception as e:
            logging.error(f"Unexpected error reading token file: {e}")
    return(token)


def request_token(config_data):
    logging.info("Requesting token")
    token = ""
    env_name = config_data['env']['name']

    request_payload = { 
        "grant_type": "password",
        "username": config_data["credentials"]["username"],
        "password": keyring.get_password(f"epc-cli_{env_name}_psswd", config_data["credentials"]["username"]),
        "client_id": keyring.get_password(f"epc-cli_{env_name}_client-id", config_data["credentials"]["username"]),
        #"client_secret": keyring.get_password(f"epc-cli_{env_name}_client-secret", config_data["credentials"]["username"]),
        "resource": config_data["env"]["resource"],
        "scope": "openid"
    }
    response = requests.post(config_data["env"]["authentication_url"], data = request_payload, verify = certifi.where())

    if response.status_code == 200:
        try:
            token = response.json().get("access_token")
        except:
            logging.debug(f"{response.status_code} | {response.text}")
            logging.error("I was not able to parse the response")
    else:
        logging.debug(f"{response.status_code} | {response.text}")
    if token == "":
        sys.exit()
    else:
        return token
