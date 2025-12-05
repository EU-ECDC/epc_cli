import sys
sys.path.insert(0, '.')
import re
import argparse
import epc_cli
import time
import json
import uuid
import zipfile
import os
import datetime

def validate_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")


def csv_upload_step(token, config_data, path_to_csv, upload_type, rp_start, rp_end):
    max_attempts = 10
    # file upload
    d_my_guid = epc_cli.upload_csv(token, config_data, path_to_csv, upload_type, rp_start, rp_end)

    print()
    i=0
    l_guids_data_ok = []
    while(i<=max_attempts):
        l_guids_data_ok = epc_cli.get_upload_save_status(token, config_data, d_my_guid)
        #print("    Attempt: {}".format(i+1))
        print()
        if l_guids_data_ok != []:
            break
        if i == max_attempts:
            print("ERROR: exceeded maximum number of attempts")
            sys.exit(3)
        i+=1
        time.sleep(5)
    
    target_guid = None
    if len(l_guids_data_ok) == 1:
        target_guid = l_guids_data_ok[0]
    elif len(l_guids_data_ok) == 2: # for subjects with a parent-child layout
        d3 = epc_cli.search_metadata_file_upload_by_guid(token, config_data, l_guids_data_ok[0])
        target_guid = l_guids_data_ok[0] if any(item.get("uploadGuid") for item in d3.get("data") or []) else l_guids_data_ok[1]
        print(f"    GUID to trigger epidemiological validation and track the status of the submission: {target_guid}")
        print()
    else:
        print("ERROR: I do not know how to handle this condition (more than two guids)")
        sys.exit(6)

    # technical validation
    b = epc_cli.start_tech_validation(token, config_data, l_guids_data_ok)
    print()
    technicalValidationJobGroupGuid=None
    j=0
    while(j<=max_attempts):
        s = epc_cli.get_upload_timeline(token, config_data, target_guid)
        #print("    Attempt: {}".format(j+1))
        print()
        if (len(s["timeLineSteps"]) > 0) and (s["timeLineSteps"][-1]["uploadState"] in ["Tech validation successful", "Tech validation failed"]):
            technicalValidationJobGroupGuid=s["technicalValidationJobGroupGuid"]
            break
        if j > max_attempts:
            print("ERROR: exceeded maximum number of attempts")
            sys.exit(4) 
        time.sleep(10)
        j+=1
    if technicalValidationJobGroupGuid:
        # getting the technical validation report
        epc_cli.get_csv_tech_validation(token, config_data, technicalValidationJobGroupGuid, f"{config_data['application_data']}/submissions/{target_guid}/technical_validation_report.csv")
        if s["timeLineSteps"][-1]["uploadState"] == "Tech validation failed":
            sys.exit(21)
    
    return(target_guid)



def epidemiological_validation_step(token, config_data, guid):
    a = 1
    max_attempts = 10
    # starting epidemiological validation
    vdata = epc_cli.start_epidemiological_validation(token, config_data, guid)
    print("    Started: {}".format(vdata["isSuccessful"]))
    print("    resultMessage: {}".format(vdata["resultMessage"]))
    print("    Epidemiological Validation GUID: {}".format(vdata["taskCorrelationGuid"]))
    print()
    if vdata["isSuccessful"] == True:
        generating_report = True
        while(generating_report):
            tl2 = epc_cli.get_upload_timeline(token, config_data, guid)
            #print(f"    Attempt {a}")
            print()
            if tl2['timeLineSteps'][-1]["statusDescription"] == "Data validation report ready":
                break
            if tl2['timeLineSteps'][-1]["statusDescription"] == "Data validation failed":
                print("ERROR: data validation failed")
                sys.exit(81)
            if a > max_attempts:
                print("ERROR: exceeded maximum number of attempts")
                sys.exit()
            a = a + 1
            time.sleep(60)
            
        # getting the epidemiological validation report
        epc_cli.get_epidemiological_validation_report(token, config_data, vdata['taskCorrelationGuid'], f"{config_data['application_data']}/submissions/{guid}/report.html")
        return(vdata["taskCorrelationGuid"])
    else:
        return(None)


def iso_validation_step(token, config_data, guid, my_regex, subject_code):
    max_attempts = 5

    tl = epc_cli.get_upload_timeline(token, config_data, guid)
    print()
    if (len(tl['timeLineSteps'])>=4) and (tl['timeLineSteps'][3]["statusDescription"] == "ISO file validation successful"):
        raise Exception("ERROR: You have already passed the ISO validation step [StatusDescription: ISO file validation successful]. ")
                                        
    epc_cli.start_iso_validation(token, 
                        config_data, 
                        guid, 
                        rf"{my_regex}",  
                        subject_code)
    print()
    j=0
    while(j<max_attempts):
        s = epc_cli.get_status_ISO_validation(token, config_data, guid)
        if s == []:
            print("    Status: Data validation ongoing")
            #print("    Attempt: {}".format(j+1))
            print()
            if j > max_attempts:
                print("ERROR: exceeded maximum number of attempts")
                sys.exit()
            time.sleep(10)
            j=j+1
        else:
            not_paired = 0
            record_ids_not_paired = [] 
            for e in s:
                if e['isPaired'] == "No":
                    not_paired += 1
                    record_ids_not_paired.append(e['recordId'])
            if not_paired:
                print("    Status: ISO validation failed")
                print("    Issue: File mappings not found for {}".format(", ".join(record_ids_not_paired)))
                sys.exit()
            else:
                print("    Status: ISO validation successful")
            break


def automate_submission(config_data: dict,
                        subject: str,
                        upload_type: str,
                        csv_xml: list | None,
                        seq_data: list | None = None,
                        has_parent_child_layout: bool = False,
                        rp_start: str | None = None, 
                        rp_end: str | None = None,
                        regex: str | None = None):
    z_archive = None
    country_code = None
    try:
        country_code = config_data["env"]["country_code"]
    except KeyError:
        raise KeyError("ERROR: I could not find the country code in your configuration data")

    # case 1: only epidemiological data
    if csv_xml and (not seq_data):

        # die if the reporting period has not been specified by the user
        if not rp_start or not rp_end:
            raise ValueError("ERROR: It is required to specify the reporting period when submitting epidemiological data.")

        if has_parent_child_layout and len(csv_xml) == 2:
            z_archive = epc_cli.zip_files(csv_xml)
            print()
            csv_xml = [z_archive]

        # each file is a different submission
        for f in csv_xml:

            token = epc_cli.request_token(config_data)
            print()
        
            csv_guid = csv_upload_step(token, config_data, f, upload_type, rp_start, rp_end)
            print()
            
            epi_valid_guid = epidemiological_validation_step(token, config_data, csv_guid)
            print()

            ndata = epc_cli.approve_reject_submission(token, config_data, epi_valid_guid, "Approve")
            print(f"    action: Approve")
            print(f"    isSuccessful: {ndata['isSuccessful']}")
            print(f"    taskCorrelationGuid: {ndata['taskCorrelationGuid']}")

                        
    # case 2: epidemiological and sequencing data
    elif csv_xml and seq_data:
        
        # die if the subject_code, country code or regex are not specified
        if not subject or not country_code or not regex:
            raise ValueError("ERROR: Specifying the subject code, country code, and regex for file mapping is mandatory when submitting sequencing data.")

        elif len(csv_xml) > 2:
            raise ValueError("ERROR: for now I can handle only one csv/xml at the time or two in case of a subject with a parent-child layout for submissions with sequencing data")

        t = epc_cli.request_token(config_data)
        print()

        # if there are two csv|xml files, I assume they follow a parent-child layout
        if len(csv_xml) == 2:
            z_archive = epc_cli.zip_files(csv_xml)
            print()
            csv_xml = [z_archive]
        
        csv_guid = csv_upload_step(token, config_data, csv_xml[0], upload_type, rp_start, rp_end)
        print()

        for fa in seq_data:
            a = epc_cli.get_s3_presigned_url(token, config_data, subject, country_code, fa)
            print()
            #print("pre-signed url: {}".format(a['fileName']))
            epc_cli.upload_with_presigned_url(config_data, fa, a['fileName'])
            print()

        iso_validation_step(token, config_data, csv_guid, regex, subject)
        print()

        epi_valid_guid = epidemiological_validation_step(token, config_data, csv_guid)
        print()

        ndata = epc_cli.approve_reject_submission(token, config_data, epi_valid_guid, "Approve")
        print(f"    action: Approve")
        print(f"    isSuccessful: {ndata['isSuccessful']}")
        print(f"    taskCorrelationGuid: {ndata['taskCorrelationGuid']}")

    else:
        print("ERROR: Unexpected combination of input files")

    # I remove the zip archive
    if z_archive and os.path.isfile(z_archive):
        os.remove(z_archive)
        print()
        print(f"Temporary zip archive {z_archive} correctly removed")
