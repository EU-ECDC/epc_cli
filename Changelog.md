## Changelog

For more recent versions please see [README.md](README.md)

0.5.1
- [fix] SSL verification enabled for request_token()
- minor changes to README and Dockerfile

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