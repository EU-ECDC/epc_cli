# EpiPulse Cases CLI

## Installation
You first need to clone the git repository and create the epc_cli conda environment:
```
git clone https://github.com/ejfresch/epc_cli.git
cd epc_cli/
mamba env create -f env/epc_cli.yaml 
```

Then you need to set up your configuration file (config.json) by adding your credentials and the urls of the resources that you will use to contact the API endpoints. 

Note: Some users might need to set up use multiple configuration files to account for for different roles, subjects and/or environments. 

## Usage

The expectation is that the scripts are ran from the epc_cli/ directory. 

### Epidemiological data

Please remember to activate the conda environment:
```
mamba activate epc_cli
```

The first step is to upload a csv and trigger the technical validation.
```
./bin/epc_upload_csv -c config-uat-HD-FR.json --upload_type "Add/Update" --files dataset/epc_Deng_tessy_2025_20240523_v1.csv --rp_start 2025-01-01 --rp_end 2025-03-27
```
Notes: 
- in case of submission of epidemiological data `--rp_start` and `--rp_end` MUST be defined. 
- By default, all scripts will try to use config.json. If you want to use another configuration file you can do so using the -c/--config option (as shown in this example).
- The technical validation report will be saved on `./submissions/{guid}/technical_validation_report.csv`.

Then you can start the epidemiological validation:
```
./bin/epc_epi_validation -c config-uat-HD-FR.json --guid 24624893-b47c-4021-8726-c2215cf73d1b
```

And finalise your data submission:
```
./bin/epc_finalise_submission -c config-uat-HD-FR.json --epi_validation_guid 4c847b0c-fc33-4f2e-b4f1-2566f566a754 --action Reject --reject_reason 'this is a test'
```

### WGS data (ISO subjects)

Please remember to activate the conda environment:
```
mamba activate epc_cli
```

The first step is to upload a csv and trigger the technical validation:
```
./bin/epc_upload_csv -c config-uat.json --upload_type "Add/Update" --files dat
aset/LEGIISO_metadata_submission-A7.csv
```
Notes: 
- By default, all scripts will try to use config.json. If you want to use another configuration file you can do so using the -c/--config option (as shown in this example).
- the technical validation report will be saved on `./submissions/{guid}/technical_validation_report.csv`.

Now we can proceed to upload the sequence data:
```
./bin/epc_upload_seq_data -c config-uat.json --subject LEGIISO -country_code NL --files dataset/*.fastq.gz
```

If the files were uploaded successfully, we can perform the ISO validation (mapping the recordIDs to the sequencing data):
```
./bin/epc_iso_validation -c config-uat.json --subject LEGIISO --guid 81c4993b-4640-4a25-a9f1-5bc37ead29b3 --regex '^(?<RecordId>[A-Z0-9\-]+)_[A-Z0-9_a-z\-]+.(fastq|fq).gz$'
```
Note: remember to put the regex on sigle quotes. In case of a failure, you may want to check your regular expression [here](https://regex101.com/).

Then we can perform the epidemiological validation:
```
./bin/epc_epi_validation -c config-uat.json --guid 81c4993b-4640-4a25-a9f1-5bc37ead29b3
```

And finalise the submission:
```
./bin/epc_finalise_submission -c config-uat.json --epi_validation_guid 4c847b0c-fc33-4f2e-b4f1-2566f566a754 --action Approve
```

## Changelog

0.2.0 [major update]
- full workflow that covers data submission of epidemiological and WGS data
- conda environment yaml file (env/epc_cli.yaml)
- README file describing software installation and usage

0.1.0
- capability to get a token, authenticate and get the list of available WGS subjects
- loading credentials and urls from a json file specified by the user (default: config.json)