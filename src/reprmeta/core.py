""" ReprMeta core.py

A python package for embedding reproducibility metadata into notebooks, 
pipelines, and scientific workflows

ReprMeta should always be run using the project root as the working directory.
Custom environment file paths must be expressed relative to the working 
directory.

Usage:

TODO

"""


import json
import util
import metadata


### Core functions --------------------------------------------------------

def get_metadata(**kwargs) -> dict:
    """ Return dict containing reproducibility metadata 
    
    If a JSON path is not specified, automatically grab reproducibility metadata
    from environment. Otherwise, return metadata specified in JSON file as dict,
    without injecting any current environment information.
    
    
    Supported keyword arguments (all optional):
    
    json: path to json file to retrieve metadata from. If not supplied,
    gets current environment metadata instead

    environment_yml: custom relative path to environment.yml-style file    
    
    """
    if kwargs.get("json", None): return(load_json(kwargs["json"]))
    env_files = util.get_env_files(kwargs)
    project_exts = util.get_project_exts()
    present_languages = util.get_present_languages(project_exts)
    
    return {
        "Versioning": {
            "ReprMeta Version": metadata.get_reprmeta_version(),
            "Timestamp": metadata.get_timestamp(),
            "Git Metadata": metadata.get_git_metadata()
        },
        "Machine Metadata": {
            "HPC Metadata": metadata.get_hpc_metadata(),
            "OS Metadata": metadata.get_os_metadata(),
            "Hardware Metadata": metadata.get_hardware_metadata(),
            "Regional Metadata": metadata.get_regional_metadata()
        },
        "Language Metadata": metadata.get_language_metadata(present_languages),
        "Environment Management": metadata.get_environment_metadata(env_files)
    }


def print_metadata() -> None:
    """ Pretty-print metadata to console """
    metadata = get_metadata()
    for key, value in metadata.items():
        if isinstance(value, str):
            print(f"\n{key}: {value}")
        elif isinstance(value, dict):
            print(f"\n{key}: ")            
            for key2, value2 in value.items():
                print(f"    {key2}: {value2}")
        else:
            print(f"\n{key}: N/A")
    print("\n")


def export_metadata(dest="", filename="reprmeta", 
                    env_file="", comments={}) -> None:
    """ Write metadata to .json file at dest file/directory """
        
    try: # Get all conda package metadata
        conda_package_dump_str = subprocess.check_output(
            ["conda", "list", "--json"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
        conda_package_dump_dict = json.loads(conda_package_dump_str)
    except:
        conda_package_dump_dict = None
    
    export_dict = {
        "generated_by": "ReprMeta",
        "schema_version": 1,
        "comments": comments,
        "reprmeta": get_metadata(env_file)
    }
    
    # Get export destination .json file
    if not dest:
        dest = os.path.join(os.getcwd(), f"{filename}.json")
    else:
        if os.path.isdir(dest):
            dest = os.path.join(dest, f"{filename}.json")
            
    # Export metadata
    with open(dest, "w", encoding="utf-8") as export_file:
        json.dump(export_dict, export_file, indent=2)