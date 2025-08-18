# EpiPulse Cases CLI

## Installation
You first need to clone the git repository and create the epc_cli conda environment:
```
git clone https://github.com/ejfresch/epc_cli.git

# For ECDC staff: you can use the devops repository
# git clone https://EU-ECDC@dev.azure.com/EU-ECDC/Bioinformatics/_git/epc_cli

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
- If your subject follows a parent-child data model, please read the sub-section "Subjects with a parent-child layout" (see below)

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

#### Subjects with a parent-child layout
Some subjects use a parent-child data model, where multiple interrelated files are required to represent a complete record submission. An example is SALMISO, where one file specifies the main information of the isolates (e.g. date and place of sampling, typing data), while a second file contains the antimicrobial resistance data linked to those isolates.

The submission process differs only slightly from standard submissions. In this specific case we 
```
./bin/epc_automatic_submission -c data/config-uat.json --upload_type "Add/Update" -f data/1.SALMISO_myupload.csv data/2.SALMISO_myupload_AST.csv --subject SALMISO --country_code NL --parent_child --rp_start 2022-04-13 --rp_end 2022-09-10
```

Notes: 
- You need to specify the `--parent_child` flag; otherwise the provided files you provide will be treated as independend submissions
- Exactly two (csv|xml) files must be provided per execution of `epc_automatic_submission`. Submitting more than two files at once (e.g., four or six files) is not supported at this stage. 
- The file with the main information on the records ("parent") must start with `1.`, while the one with additional information ("child") must start with a `2.`  

In this example, we did not run epc_automatic_submission with the --approve flag. This flag automatically approves a data submission once it successfully completes all the steps in the workflow, providing full automation of the submission process. While using this flag fully automates the submission, it is highly recommended to review the epidemiological validation report before approving or rejecting the submission.

The epidemiological validation report can be found on `{submission_data}/submissions/{guid}/`. 

If you now wish to approve the data submission, you can do so with the following command:
```
./bin/epc_finalise_submission -c data/config-uat.json --epi_validation_guid 95b955c3-bc54-4f6b-b521-7cb704504a31 --action Approve
```

Notes:
- you will find the epi_validation_guid in the output of epc_automatic_submission 

If you wish to reject the data submisson, you can do so with the following command:
```
./bin/epc_finalise_submission -c config-uat.json --epi_validation_guid 95b955c3-bc54-4f6b-b521-7cb704504a31 --action Reject --reject_reason 'this is only a test'
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

#### Subjects with a parent-child layout
Some subjects use a parent-child data model, where multiple interrelated files (csv, xml) are required to represent a complete record submission. An example is SALMISO, where one file specifies the main information of the isolates (e.g. date and place of sampling, typing data), while a second file contains the antimicrobial resistance data linked to those isolates.

In this case you need to submit two csv or xml files as well as the fastq or fasta files with the sequencing data.

The submission process differs only slightly from standard submissions.  
```
./bin/epc_automatic_submission -c data/config-uat.json --upload_type "Add/Update" -f data/1.SALMISO_myupload.csv data/2.SALMISO_myupload_AST.csv data/28382022* data/11402022* --subject SALMISO --country_code NL --parent_child --rp_start 2022-04-13 --rp_end 2022-
09-10
```

Notes: 
- You need to specify the `--parent_child` flag; otherwise the provided files you provide will be treated as independend submissions
- Exactly two (csv|xml) files must be provided per execution of `epc_automatic_submission`. Submitting more than two files at once (e.g., four or six files) is not supported at this stage. 
- The file with the main information on the records ("parent") must start with `1.`, while the one with additional information ("child") must start with a `2.`  

In this example, we did not run epc_automatic_submission with the --approve flag. This flag automatically approves a data submission once it successfully completes all the steps in the workflow, providing full automation of the submission process. While using this flag fully automates the submission, it is highly recommended to review the epidemiological validation report before approving or rejecting the submission.

The epidemiological validation report can be found on `{submission_data}/submissions/{guid}/`. 

If you now wish to approve the data submission, you can do so with the following command:
```
./bin/epc_finalise_submission -c data/config-uat.json --epi_validation_guid 95b955c3-bc54-4f6b-b521-7cb704504a31 --action Approve
```

Notes:
- you will find the epi_validation_guid in the output of epc_automatic_submission 

If you wish to reject the data submisson, you can do so with the following command:
```
./bin/epc_finalise_submission -c config-uat.json --epi_validation_guid 95b955c3-bc54-4f6b-b521-7cb704504a31 --action Reject --reject_reason 'this is only a test'
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

#### epc_cli and Docker
If you prefer to use a docker container to run epc_cli, we provide a dockerfile (`docker/Dockerfile_epc_cli.prod`) that you can use to build an image. 

You can build the image using the following command:
```
docker build . -f docker/Dockerfile_epc_cli.prod --tag [your_namespace]/epc_cli:[version] --no-cache
```
For instance, in our case this is:
```
docker build . -f docker/Dockerfile_epc_cli.prod --tag ejfresch/epc_cli:0.5.1 --no-cache
```


Then you can execute the commands described in the 'Usage' section, using the following syntax:
```
docker run -it --rm --volume $(pwd):/tmp --workdir /tmp --user $(id -u):$(id -g) ejfresch/epc_cli:0.5.1 [my_command]
```
Note: please remember to change the tag according to your namespace and the version of epc_cli you are using

For instance, if you want to submit a csv file with case data, you should type
```
docker run -it --rm --volume $(pwd):/tmp --workdir /tmp --user $(id -u):$(id -g) ejfresch/epc_cli:0.5.1 epc_automatic_submission --config config-uat-HD-FR.json --upload_type "Add/Update" --files dataset/epc_Deng_tessy_2025_20240523_v1.csv --rp_start 2025-01-01 --rp_end 2025-03-27
```

## Changelog
0.5.1
- README and Dockerfile updated

0.5.0
- support for subjects with a parent-child layout

0.4.1
- [fix] SSL verification is now enabled (previously verify = False)  

0.4.0
- added dockerfile to generate a docker image for epc_cli

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