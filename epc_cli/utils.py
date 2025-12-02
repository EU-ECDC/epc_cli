
import os
import json

def load_metadata(json_file):
    metadata = {}
    # reading the configuration file
    if os.path.isfile(json_file):
        with open(json_file, 'r') as j:
            metadata = json.load(j)
        return(metadata)
    else:
        raise Exception(f"ERROR: I cannot find {json_file}")

def save_metadata(dict_metadata, target_json):
    with open(target_json, "w") as inp:
        json.dump(dict_metadata, inp, indent=4)
   
