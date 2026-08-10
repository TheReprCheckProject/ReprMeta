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
from importlib.metadata import version, PackageNotFoundError

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

def get_reprmeta_version():
    """ Get current package version if installed """
    try:
        return version("reprmeta")
    except PackageNotFoundError:
        return None


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

        return {"Latest Commit": commit, "Git Branch": branch, 
                "Dirty Repo": bool(status), "Git Remote URL": remote_url}

    except Exception:
        return None


def get_hardware_metadata():
    """ Get machine, architecture, number of cores, and processor name """
    return {"Machine": platform.machine(),
            "Architecture": platform.architecture()[0],
            "Number of Logical Cores": os.cpu_count(),
            "Processor": platform.processor()}


def get_os_metadata():
    """ Get operating system, release, and OS version """
    return {
        "OS": platform.system(),
        "OS Release": platform.release(),
        "OS Version": platform.version(),
    }    


def get_python_metadata():
    """ Get Python version and implementation """
    return {
        "Python Version": sys.version,
        "Python Implementation": platform.python_implementation()
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
            "Conda Present": conda_present,
            "Conda Channels": channels,
            "Conda Dependencies": dependencies
        }

    return None


def get_hpc_metadata():
    """ Get HPC job scheduler """
    hpc_env_vars = {
        "Slurm": "SLURM_JOB_ID",
        "PBS": "PBS_JOBID",
        "LSF": "LSB_JOBID",
        "SGE": "JOB_ID",
        "HTCondor": "CONDOR_JOBID",
        "AWS Batch": "AWS_BATCH_JOB_ID",
        "Google Cloud Batch": "GOOGLE_CLOUD_BATCH_JOB",
        "Azure Batch": "AZ_BATCH_JOB_ID",
    }

    for scheduler, env_var in hpc_env_vars.items():
        if os.environ.get(env_var):
            return scheduler
    return None


def get_misc_metadata():
    """ Get locale and encoding """
    return {
        "Locale": locale.getlocale()[0], 
        "Encoding": locale.getlocale()[1]
    }




### Core functions --------------------------------------------------------

def get_metadata(env_file="") -> dict:
    """ Create dict containing comprehensive reproducibility metadata """
    return {
        "ReprMeta Version": get_reprmeta_version(),
        "Timestamp": get_timestamp(),
        "Git Metadata": get_git_metadata(),
        "Hardware Metadata": get_hardware_metadata(),
        "OS Metadata": get_os_metadata(),
        "Python Metadata": get_python_metadata(),
        "Conda Metadata": get_conda_metadata(env_file),
        "HPC Metadata": get_hpc_metadata(),
        "Misc Metadata": get_misc_metadata()
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
        elif isinstance(value, dict):
            print(f"\n{key}: ")            
            for key2, value2 in value.items():
                print(f"    {key2}: {value2}")
        else:
            print(f"\n{key}: N/A")
    print("\n")


def export_metadata(dest="", filename="reprmeta"):
    """ Write metadata to .json file at dest file/directory """
    # conda list --json lists all packages in the environment - use for export    
    raise NotImplementedError