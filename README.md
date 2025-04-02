# EpiPulse Cases CLI

## Installation
You first need to clone the git repository and create the epc_cli conda environment:
```
git clone https://github.com/ejfresch/epc_cli.git
cd epc_cli/
mamba env create -f env/epc_cli.yaml 
```

Then you need to set up your configuration file (config.json) by adding your credentials, the urls of the resources that you will use to contact the API endpoints and optional customisations. 

Note: Some users might need to set up use multiple configuration files to account for for different roles, subjects and/or environments. 

## Usage
This software package provides both a single script, epc_automatic_submission, designated to automate the submission process as much as possible, as well as a set of scripts which allow users to go through the workflow step by step. In this section we will use epc_automatic_submission to submit data. 

Note: an assumption in all commands shown in this guide is that the scripts are ran from the epc_cli directory. 

### Epidemiological data

Please remember to activate the conda environment:
```
mamba activate epc_cli
```

Then we can submit a csv file with case data:
```
./bin/epc_automatic_submission --config config-uat-HD-FR.json --upload_type "Add/Update" --files dataset/epc_Deng_tessy_2025_20240523_v1.csv --rp_start 2025-01-01 --rp_end 2025-03-27
```

Notes: 
- in case of submission of epidemiological data `--rp_start` and `--rp_end` MUST be defined. 
- the upload type string is case sensitive. "Add/Update" works, "add/update" does not.
- By default, epc_automatic_submission looks for a config.json file in the current directory. If you have set up and intend to use this file, there is no need to specify it explicitly with the -c/--config option. However, if you prefer to use a different configuration file, you can specify it using the -c/--config option, as shown in this example.
- The technical validation and epidemiological validation reports will be saved on `{submission_data}/submissions/{guid}/`. The default submission_data folder is the current directory (`./`).

In this example, we did not run epc_automatic_submission with the --approve flag. This flag automatically approves a data submission once it successfully completes all the steps in the workflow, providing full automation of the submission process. While using this flag fully automates the submission, it is highly recommended to review the epidemiological validation report before approving or rejecting the submission.

The epidemiological validation report can be found on `{submission_data}/submissions/{guid}/`. 

If you now wish to approve the data submission, you can do so with the following command:
```
./bin/epc_finalise_submission -c config-uat-HD-FR.json --epi_validation_guid 4c847b0c-fc33-4f2e-b4f1-2566f566a754 --action Approve
```

Notes:
- you will find the epi_validation_guid in the output of epc_automatic_submission 

If you wish to reject the data submisson, you can do so with the following command:
```
./bin/epc_finalise_submission -c config-uat-HD-FR.json --epi_validation_guid 4c847b0c-fc33-4f2e-b4f1-2566f566a754 --action Reject --reject_reason 'this is only a test'
```

### WGS data (ISO subjects)

Please remember to activate the conda environment:
```
mamba activate epc_cli
```

Then we can submit sequencing data and the csv with the associated metadata:
```
./bin/epc_automatic_submission -c config-uat.json --upload_type "Add/Update" -f dataset/LEGIISO_metadata_submission-A10.csv dataset/*-test8.fastq.gz --subject LEGIISO --country_code NL --regex '^(?<RecordId>[A-Z0-9\-]+)_[A-Z0-9_a-z\-]+.(fastq|fq).gz$'
```

Notes:
- In case of submission for an ISO subject `--subject` and `--country_code` and `--regex` MUST be defined. 
- Remember to put the regular expression on sigle quotes (as shown above). In case of a issues, you may want to check your regular expression [here](https://regex101.com/).
- By default, epc_automatic_submission looks for a config.json file in the current directory. If you have set up and intend to use this file, there is no need to specify it explicitly with the -c/--config option. However, if you prefer to use a different configuration file, you can specify it using the -c/--config option, as shown in this example.
- The technical validation and epidemiological validation reports will be saved on `{submission_data}/submissions/{guid}/`. The default submission_data folder is the current directory (`./`).



In this example, we did not run epc_automatic_submission with the --approve flag. This flag automatically approves a data submission once it successfully completes all the steps in the workflow, providing full automation of the submission process. While using this flag fully automates the submission, it is highly recommended to review the epidemiological validation report before approving or rejecting the submission.

The epidemiological validation report can be found on `{submission_data}/submissions/{guid}/`. 

If you now wish to approve the data submission, you can do so with the following command:
```
./bin/epc_finalise_submission -c config-uat-HD-FR.json --epi_validation_guid 4c847b0c-fc33-4f2e-b4f1-2566f566a754 --action Approve
```

Notes:
- you will find the epi_validation_guid in the output of epc_automatic_submission 

If you wish to reject the data submisson, you can do so with the following command:
```
./bin/epc_finalise_submission -c config-uat-HD-FR.json --epi_validation_guid 4c847b0c-fc33-4f2e-b4f1-2566f566a754 --action Reject --reject_reason 'this is only a test'
```

### Advanced usage

You can use this software package as a library to build your own scripts.

Here is an example that shows how you can get information on your user permissions: 
```
import epc_cli
config_data = epc_cli.load_config("./config-uat.json")
token = epc_cli.request_token(config_data)

epc_cli.get_user_permissions(token, config_data)
```

which gives the following output:
```
{'hasEpipulseCasesPermission': True, 'hasWGSSubjectsPermission': True, 'hasUploadPermission': True, 'hasApprovePermission': True, 'hasAnyNonWGSUploadPermission': False, 'hasAnyWGSUploadPermission': True, 'hasAnyAllowWebEntryUploadPermission': False}
```


## Changelog

0.3.0
- improved automation features
  - the user can use a single command to trigger the full workflow instead of typing a separate command for each step of the workflow
  - the user can provide a list of files \[csv|xml|fasta|fastq.gz|fq.gz\] and the system will autodetect the steps of the workflow which are needed to finalise that specific data submission  
  - the user can trigger the automatic approval of a submission through the --approve option. If the user does not intend to use such option, he/she has to manually execute epc_finalise_submission to approve or reject the data submission
- changes to the configuration file 
  - the user can choose an arbitrary folder where to store the data associated with the submissions (technical validation and epidemiological validation reports).

0.2.0
- full set of functions to cover the API calls used for data submission
- full workflow that covers data submission of epidemiological and WGS data
- conda environment yaml file (env/epc_cli.yaml)
- README file describing software installation and usage

0.1.0
- capability to get a token, authenticate and get the list of available WGS subjects
- loading credentials and urls from a json file specified by the user (default: config.json)