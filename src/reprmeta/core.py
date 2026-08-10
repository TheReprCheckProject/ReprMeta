""" ReprMeta

A python package for embedding reproducibility metadata into notebooks, 
pipelines, and scientific workflows

Usage:

- Jupyter example
-- reprmeta.metadata() is an alias for reprmeta.get_metadata() which
-- returns a dict of metadata
import reprmeta
reprmeta.metadata()

- General metadata print example
import reprmeta
reprmeta.print_metadata()

- Metadata export example
import reprmeta
reprmeta.export_metadata("path/to/destination.json")

- Specific metadata retrieval examples
import reprmeta
reprmeta.get_python_version()
reprmeta.get_platform_metadata()
reprmeta.get_git_metadata()

"""

import sys
import locale
import os
import platform
import subprocess
from datetime import datetime

import yaml



### Future functions to implement -----------------------------------------

def get_venv_metadata():
    # In active venv environment bool
    raise NotImplementedError


def get_docker_metadata():
    # Running in docker container bool
    raise NotImplementedError


def get_virtual_env_metadata():
    # Cloud instance detection bool
    raise NotImplementedError




### Get metadata functions ------------------------------------------------

def get_timestamp():
    return datetime.now().isoformat()


def get_git_metadata():
    """ If inside git repo, get git commit hash, branch, and repo status """
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()

        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        remote_url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"]
        ).decode().strip()

        return {"git_commit": commit, "git_branch": branch, 
                "is_dirty": bool(status), "git_remote_url": remote_url}

    except Exception:
        return {}


def get_hardware_metadata():
    """ Get machine, architecture, number of cores, and processor name """
    return {"machine": platform.machine(),
            "architecture": platform.architecture()[0],
            "num_cores": os.cpu_count(),
            "processor": platform.processor()}


def get_os_metadata():
    """ Get operating system, release, and OS version """
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
    }    


def get_python_metadata():
    """ Get Python version and implementation """
    return {
        "python_version": sys.version,
        "python_implementation": platform.python_implementation()
    }


def get_conda_metadata(env_file):
    """ Get whether conda is present and if so, packages in environment.yml """
    if os.environ.get("CONDA_DEFAULT_ENV"):
        conda_present, channels, dependencies = True, [], []
        
        if not env_file:
            # Attempt to locate environment.yml in current working directory
            path = os.path.join(os.get_cwd(), "environment.yml")
            env_file = path if os.path.isfile(path) else ""

        if env_file: # Parse environment.yml
            with open(env_file, "r") as file:
                data = yaml.safe_load(file)
            channels = sorted(data["channels"])
            raw_dependencies = data["dependencies"]
            for dependency in raw_dependencies:
                if isinstance(dict, dependency) and "pip" in dependency: 
                    dependencies.extend(item["pip"]) # pip install section
                else:
                    dependencies.append(item)
            dependencies = sorted(dependencies)
            
        return {
            "conda_present": conda_present,
            "conda_channels": channels,
            "conda_dependencies": dependencies
        }
            
    return None


def get_hpc_metadata():
    """ Get HPC job scheduler """
    hpc_env_vars = {
        "slurm": "SLURM_JOB_ID",
        "pbs": "PBS_JOBID",
        "lsf": "LSB_JOBID",
        "sge": "JOB_ID",
        "htcondor": "CONDOR_JOBID",
        "aws_batch": "AWS_BATCH_JOB_ID",
        "gcp_batch": "GOOGLE_CLOUD_BATCH_JOB",
        "azure_batch": "AZ_BATCH_JOB_ID",
    }

    for scheduler, env_var in hpc_env_vars.items():
        if os.environ.get(env_var):
            return scheduler
    return None


def get_misc_metadata():
    """ Get locale and encoding """
    return {
        "locale": locale.getlocale(), 
        "encoding": sys.getfilesystemencoding()
    }




### Core functions --------------------------------------------------------

def get_metadata(env_file="") -> dict:
    """ Create dict containing comprehensive reproducibility metadata """
    return {
        "timestamp": get_timestamp(),
        "git_metadata": get_git_metadata(),
        "hardware_metadata": get_hardware_metadata(),
        "os_metadata": get_os_metadata(),
        "python_metadata": get_python_metadata(),
        "conda_metadata": get_conda_metadata(env_file),
        "hpc_metadata": get_hpc_metadata(),
        "misc_metadata": get_misc_metadata()
    }


def metadata() -> dict:
    """ Alias for get_metadata() """
    return get_metadata()


def print_metadata():
    """ Pretty-print metadata to console """
    metadata = get_metadata()
    for key, value in metadata.items():
        if isinstance(value, str):
            print(f"\n{key}: {value}")
            
        if isinstance(value, dict):
            print(f"\n{key}: ")            
            for key2, value2 in value.items():
                print(f"    {key2}: {value2}")
    print("\n")


def export_metadata(dest="", filename="reprmeta"):
    """ Write metadata to .json file at dest file/directory """
    # conda list --json lists all packages in the environment - use for export    
    raise NotImplementedError