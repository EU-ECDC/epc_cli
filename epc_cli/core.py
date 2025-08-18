import os
import requests
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from requests_toolbelt import MultipartEncoder
import json
from tqdm import tqdm
import pandas as pd
import logging
import base64
import certifi
import uuid
import zipfile

def zip_files(file_list):
    if len(file_list) != 2:
        raise ValueError("ERROR: Exactly two files must be provided.")

    basenames = [os.path.basename(f) for f in file_list]

    # Check that one starts with 1. and the other with 2.
    if not (any(name.startswith("1.") for name in basenames) and 
            any(name.startswith("2.") for name in basenames)):
        raise ValueError("ERROR: Files must be named starting with '1.' (parent) and '2.' (child) respectively.")

    random_name = f"{uuid.uuid4().hex}.zip"
    output_zip_path = os.path.join(".", random_name)

    logging.info(f"Generating temporary zip archive {output_zip_path}")

    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        for file_path in file_list:
            if os.path.isfile(file_path):
                zipf.write(file_path, arcname=os.path.basename(file_path))
            else:
                raise FileNotFoundError(f"ERROR: {file_path} does not exist or is not a file.")

    return output_zip_path

def search_metadata_file_upload_by_guid(token, config_data, upload_guid):

    logging.info(f"Retrieving file upload metadata for GUID {upload_guid}")

    endpoint = config_data["env"]["base_url_endpoint"] + "/api/v1/DataUploadAPI/Uploads/SearchData"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    payload = {
        "skip": 0,
        "take": 10,
        "requireTotalCount": False,
        "filter": [["uploadGuid", "=", upload_guid]],
        "onlySubmittedByMe": True
    }

    params = {k: json.dumps(v) if isinstance(v, (list, dict, bool)) else v
              for k, v in payload.items()}

    response = requests.get(endpoint, headers=headers, params=params, verify=certifi.where())

    if response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            logging.error("Could not parse JSON from response")
            logging.error(response.text)
            raise e
    else:
        raise Exception(f"status_code:{response.status_code}; response:{response.text}")



def get_all_wgs_subjects(token, config_data):
    headers = {
        'Authorization': "Bearer {}".format(token)
    }
    endpoint = config_data["env"]["base_url_endpoint"] + "/api/v1/DataUploadAPI/AllWGSSubjects"
    response = requests.get(endpoint, headers=headers, verify=certifi.where())
    if response.status_code == 200:
        try:
            wgs_subjects = response.json()
            return wgs_subjects
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")


def get_user_permissions(token, config_data):
    headers = {
        'Authorization': "Bearer {}".format(token)
    }
    endpoint = config_data["env"]["base_url_endpoint"] + "/api/v1/DataUploadAPI/UserPermissions"
    response = requests.get(endpoint, headers=headers, verify = certifi.where())
    if response.status_code == 200:
        try:
            wgs_subjects = response.json()
            return wgs_subjects
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code} | reponse:{response.text}")

def upload_csv_tech_validation(token, config_data, csv_file, upload_type, rp_start = None, rp_end = None):
    
    # reading the csv file
    if os.path.isfile(csv_file):
        with open(csv_file, 'rb') as f:
            csv_data = f.read()
    else:
        raise Exception(f"{csv_file} not found")

    # request to upload the file
    basename_csv = os.path.basename(csv_file)
    x_file_identifier = f"{basename_csv.replace(".", "")}-{len(csv_data)}-{datetime.now().isoformat().split("T")[0].replace("-", "")}"
    print(x_file_identifier)
    headers = {
        "Authorization": "Bearer {}".format(token),
        "X-File-Identifier": "{}_".format(basename_csv)
    }
    payload = {
        "start": rp_start,
        "end": rp_end,
        "uploadType": upload_type,
        "ignoreDateStartEnd": True
    }
    files={'file': (basename_csv, csv_data)}
    if rp_start and rp_end: 
        payload["ignoreDateStartEnd"] = False

    endpoint = config_data["env"]["base_url_endpoint"] + "/api/v1/DataUploadAPI/Uploads"
    print(endpoint)
    print(headers)
    print(payload)

    #print(json.dumps(payload))
    response = requests.post(endpoint, headers=headers, files=payload, verify = certifi.where())
    if response.status_code == 200:
        try:
            upload_msg = response.json()
            return upload_msg
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")


def upload_csv(token, config_data, csv_file, upload_type, rp_start = None, rp_end = None):
    
    logging.info(f"Uploading files(s)")
    print(f"    Filename: {csv_file}")
    # reading the csv file
    if os.path.isfile(csv_file):
        file_size = os.path.getsize(csv_file)
        with open(csv_file, 'rb') as f:
            csv_data = f.read()
    else:
        raise Exception(f"{csv_file} not found")

    # request to upload the file
    basename_csv = os.path.basename(csv_file)
    x_file_identifier = f"{basename_csv.replace(".", "")}-{len(csv_data)}-{datetime.now().isoformat().split("T")[0].replace("-", "")}"
    #print(x_file_identifier)

    ignore_date_start_end = True
    if rp_start and rp_end: 
        ignore_date_start_end = False
    
    encoder = MultipartEncoder({
        "start": str(rp_start),
        "end": str(rp_end),
        "uploadType": upload_type,
        "ignoreDateStartEnd": str(ignore_date_start_end),
        'uploadFile': (basename_csv, open(csv_file, 'rb'), 'text/csv'),
        'chunkMetadata': json.dumps({
            'chunkCount': "1",
            'chunkIndex': "0",
            'chunkBlobSize': str(file_size)
        })
    })

    endpoint = config_data["env"]["base_url_endpoint"] + "/api/v1/DataUploadAPI/Uploads"
    #print(endpoint)
    headers = {"Authorization": "Bearer {}".format(token), 
        'Content-Type': encoder.content_type,
        "X-File-Identifier": basename_csv + "_"
    }
    #print(headers)


    #print(encoder)
    response = requests.post(endpoint, headers = headers, data = encoder, verify = certifi.where())
    
    if response.status_code == 200:
        try:
            upload_msg = response.json()
            print("    GUIDs dict: {}".format(upload_msg))
            return upload_msg
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")




def get_upload_save_status(token, config_data, d_guids):
    logging.info(f"Checking if data have been saved successfully in the db")

    endpoint = config_data["env"]["base_url_endpoint"] + "/api/v1/DataUploadAPI/Uploads/UploadSaveStatus"
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }

    payload = list(d_guids.values())
    response = requests.post(endpoint, headers = headers, json = payload, verify = certifi.where())
    if response.status_code == 200:
        try:
            upload_msg = response.json()
            print("    GUIDs: [{}]".format(",".join(upload_msg)))
            return upload_msg
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")


def start_tech_validation(token, config_data, l_guids):
    logging.info(f"Starting technical validation")
 
    endpoint = config_data["env"]["base_url_endpoint"] + "/api/v1/DataUploadAPI/TechnicalValidations"
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }
    payload = {
        "uploadGuids": l_guids,
        "autoStartEpidemiologicalValidation": True
    }
    response = requests.post(endpoint, headers = headers, json = payload, verify = certifi.where())
    if response.status_code == 200:
        try:
            upload_msg = response.json()
            print("    technicalValidationJobGroupCount: {}".format(upload_msg['technicalValidationJobGroupCount']))
            return upload_msg
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")

def get_csv_tech_validation(token, config_data, tech_validation_job_group_guid, path_csv_report):
    logging.info(f"Downloading technical validation report")
    dir_struct = os.path.dirname(path_csv_report)
    os.makedirs(dir_struct, exist_ok=True)
    endpoint = config_data["env"]["base_url_endpoint"] + f"/api/v1/DataUploadAPI/TechnicalValidations/{tech_validation_job_group_guid}/Results/Csv"
    headers = {
        "Authorization": "Bearer {}".format(token),
    }
    response = requests.get(endpoint, headers = headers,  verify = certifi.where(), stream = True)
    if response.status_code == 200:
        try:
            print(f"    Writing down report on {path_csv_report}")
            with open(f"{path_csv_report}", "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")


def get_upload_timeline(token, config_data, upload_guid):
    logging.info("Checking the status of the submission")
    endpoint = config_data["env"]["base_url_endpoint"] + f"/api/v1/DataUploadAPI/Upload/GetTimeline/{upload_guid}"
    #print(endpoint)
    headers = {
        "Authorization": "Bearer {}".format(token),
    }
    response = requests.get(endpoint, headers = headers, verify = certifi.where())
    if response.status_code == 200:
        try:
            upload_msg = response.json()
            #print(upload_msg)
            if len(upload_msg["timeLineSteps"]) > 0:
                print("    uploadState: {}".format(upload_msg["timeLineSteps"][-1]["uploadState"]))
            else:
                print("    uploadState: NA")
            return upload_msg
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")


def get_s3_presigned_url(token, config_data, subject_code, country_code, file_name):
    logging.info(f"Fetching S3 presigned url")
    if not os.path.exists(file_name):
        raise Exception("ERROR: the file {} does not exists".format(file_name))

    headers = {
        'Authorization': "Bearer {}".format(token)
    }
    basename = os.path.basename(file_name)
    endpoint = config_data["env"]["base_url_endpoint"] + f"/api/v1/DataUploadAPI/WGS-Upload/{subject_code}/{country_code}/{basename}"
    #print(endpoint)
    response = requests.get(endpoint, headers=headers, verify = certifi.where())
    if response.status_code == 200:
        try:
            s3_url_data = response.json()
            #print(s3_url_data)
            if "fileName" in s3_url_data:
                print("    fileName: [...]{}".format(s3_url_data["fileName"][-10:]))
            return s3_url_data
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")


def upload_with_presigned_url(config_data, file_path, presigned_url, chunk_size=1048576):
    logging.info(f"File upload - {file_path}")
    headers = {
        "x-amz-meta-uploadedby": config_data["credentials"]["username"].upper()

    }

    """
    Upload a file to an S3 bucket using a pre-signed URL with a progress bar.

    :param file_path: Path to the file to upload.
    :param presigned_url: Pre-signed URL for the S3 object.
    :param chunk_size: the file will be uploaded in chunks. This sets the chunk size (default: 1MB)
    """
    with open(file_path, 'rb') as file:
        # Get the file size to use for the progress bar
        file_size = len(file.read())
        file.seek(0)  # Reset the file pointer to the beginning

        # Initialize the progress bar
        with tqdm(total=file_size, unit='B', unit_scale=True, desc='    Status') as pbar:
            def upload_chunk(size=chunk_size):
                """
                Read and upload file in chunks, updating the progress bar.
                """
                while True:
                    chunk = file.read(size)
                    if not chunk:
                        break
                    response = requests.put( presigned_url, data=chunk, headers=headers, verify=certifi.where())
                    pbar.update(len(chunk))  # Update the progress bar
                    if response.status_code != 200:
                        raise Exception(f"Failed to upload file. Status code: {response.status_code}, Response: {response.text}")

            # Upload the file in chunks
            upload_chunk()

        print("    File uploaded successfully!")


def get_naming_conventions_by_subject_code(token, config_data, subject_code, output_file):
    logging.info(f"Fetching the naming conventions for {subject_code}")
    endpoint = config_data["env"]["base_url_endpoint"] + f"/api/v1/DataUploadAPI/NamingConventions/Preferred/{subject_code}"
    headers = {
        "Authorization": "Bearer {}".format(token),
    }
    response = requests.get(endpoint, headers = headers, verify = certifi.where())
    if response.status_code == 200:
        try:
            tab = pd.DataFrame(response.json())
            print(f"    Writing {output_file}")
            if output_file.endswith(".csv"):
                tab.to_csv(output_file, index=False)
            elif output_file.endswith(".xlsx"):
                tab.to_excel(output_file, index=False)
            #print(tab.head())
            #print(tab[["example","namingConventionTypeId","regularExpression"]])
        except:
            print("ERROR: I could not parse the response")
            print(response.text )
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")

def start_iso_validation(token, config_data, upload_guid, reg_expr, subject_code):
    logging.info(f"Starting ISO validation")
    print(f"    guid: {upload_guid}")
    print(f"    regex: {reg_expr}")
    naming_conv_type_id = None
    if reg_expr.endswith(("fq.gz", "fastq.gz", "fq.gz$", "fastq.gz$",".(fastq|fq).gz$", '\.(fastq|fq)\.gz$')):
        naming_conv_type_id = 1
    elif reg_expr.endswith(("fasta", "fa", "fa$", "fasta$", ".(fasta|fa)$", '\.(fasta|fa)\.gz$')):
        naming_conv_type_id = 2
    else:
        raise Exception(f"ERROR: cannot determine the naming convention type id")
    endpoint = config_data["env"]["base_url_endpoint"] + f"/api/v1/DataUploadAPI/WGS/{upload_guid}/FileMapping"
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }
    payload = {
        "namingConventions": [{
            "fileName": f"{upload_guid}",
            "namingConventionTypeId": f"{naming_conv_type_id}",
            "subjectCode": f"{subject_code}",
            "regularExpression": f"{reg_expr}"
        }]
    }
    #print(payload)
    response = requests.post(endpoint, headers = headers, json = payload, verify = certifi.where())
    if response.status_code == 200:
        try:
            upload_msg = response.json()
            return upload_msg
        except:
            print("ERROR: I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")


def get_status_ISO_validation(token, config_data, upload_guid):
    logging.info(f"Getting status ISO validation")
    headers = {
        'Authorization': "Bearer {}".format(token)
    }
    endpoint = config_data["env"]["base_url_endpoint"] + f"/api/v1/DataUploadAPI/Uploads/{upload_guid}/Records"
    response = requests.get(endpoint, headers=headers, verify = certifi.where())
    if response.status_code == 200:
        try:
            response_msg = response.json()
            return response_msg
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")


def search_uploads(token, config_data, skip=0, take=10, filters=None, sort=None, only_submitted_by_me=False):
    logging.info("Searching uploads")

    endpoint = config_data["env"]["base_url_endpoint"] + "/api/v1/DataUploadAPI/Uploads/SearchData"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Prepare payload according to DevExtreme LoadOptions spec
    payload = {
        "skip": skip,
        "take": take,
        "requireTotalCount": True,
        "onlySubmittedByMe": only_submitted_by_me
    }

    if filters:
        payload["filter"] = filters
    if sort:
        payload["sort"] = sort

    # For GET, we'll URL-encode the JSON payload
    params = {k: json.dumps(v) if isinstance(v, (list, dict, bool)) else v for k, v in payload.items()}

    response = requests.get(endpoint, headers=headers, params=params, verify=certifi.where())

    if response.status_code == 200:
        try:
            return response.json()
        except Exception:
            logging.error("Could not parse JSON response")
            logging.debug(response.text)
            return None
    else:
        raise Exception(f"status_code:{response.status_code}; response:{response.text}")


def start_epidemiological_validation(token, config_data, upload_guid):
    logging.info("Starting epidemiological validation")
    endpoint = config_data["env"]["base_url_endpoint"] + f"/api/v1/DataUploadAPI/EpidemiologicalValidations"
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }
    payload = {
        "uploadGuids": [upload_guid]
    }
    response = requests.post(endpoint, headers = headers, json = payload, verify = certifi.where())
    if response.status_code == 200:
        try:
            response_msg = response.json()
            return response_msg
        except:
            print("ERROR: I could not parse the response")
            print(response.text)
    elif response.status_code == 409:
        raise Exception(f"status_code:{response.status_code}; ERROR: conflict ({response.text}). Another epidemiological validation needs some actions from your side or there is an ongoing metadata synchronization")
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")


def get_status_epidemiological_validation(token, config_data, subject_code):
    logging.info(f"Getting status ISO validation")
    headers = {
        'Authorization': "Bearer {}".format(token)
    }
    endpoint = config_data["env"]["base_url_endpoint"] + f"/api/v1/DataUploadAPI/EpidemiologicalValidations/OngoingStatus/{subject_code}"
    response = requests.get(endpoint, headers=headers, verify = certifi.where())
    if response.status_code == 200:
        try:
            response_msg = response.json()
            return response_msg
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")

def get_epidemiological_validation_report(token, config_data, epi_validation_guid, path_html_report):
    logging.info(f"Getting epidemiological validation report")

    dir_struct = os.path.dirname(path_html_report)
    os.makedirs(dir_struct, exist_ok=True)

    headers = {
        'Authorization': "Bearer {}".format(token)
    }
    endpoint = config_data["env"]["base_url_endpoint"] + f"/api/v1/DataUploadAPI/EpidemiologicalValidations/{epi_validation_guid}/Report/report.html"
    response = requests.get(endpoint, headers=headers, verify = certifi.where())
    if response.status_code == 200:
        try:
            response_msg = response.json()
            print(f"    Writing down report on {path_html_report}")
            with open(path_html_report, "w") as outf:
                outf.write(base64.b64decode(response_msg).decode("utf-8"))
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")
    

def approve_reject_submission(token, config_data, epi_validation_guid, action, reject_reason_msg = ""):
    logging.info(f"User decision on data submission")


    headers = {
        'Authorization': "Bearer {}".format(token)
    }
    endpoint = config_data["env"]["base_url_endpoint"] + f"/api/v1/DataUploadAPI/EpidemiologicalValidations/SubmitEpiValidationReport"
    payload = {
        "epidemiologicalValidationGuid": epi_validation_guid,
        "action": action,
        "rejectReasonMessage": reject_reason_msg
    }
    
    response = requests.post(endpoint, headers=headers, json = payload, verify = certifi.where())
    if response.status_code == 200:
        try:
            response_msg = response.json()
            return(response_msg)
        except:
            print("[ERROR] I could not parse the response")
            print(response.text)
    else:
        raise Exception(f"status_code:{response.status_code}; reponse:{response.text}")