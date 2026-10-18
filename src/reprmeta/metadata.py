""" ReprMeta metadata.py 

Dedicated automated metadata retrieval functions.

"""

import sys
import locale
import os
import platform
import subprocess
from datetime import datetime
from importlib.metadata import version, PackageNotFoundError
import yaml



### Version control metadata ----------------------------------------------

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




### Machine metadata ------------------------------------------------------

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
    raise NotImplementedError
   # return None


def get_regional_metadata():
    """ Get locale and encoding (tend to be region-specific) """
    return {
        "Locale": locale.getlocale()[0], 
        "Encoding": locale.getlocale()[1]
    }




### Language Metadata -----------------------------------------------------

def get_language_metadata(languages) -> dict:
    """ For each language, get version and implementation data """
    raise NotImplementedError


def get_python_metadata():
    """ DEPRECATED IN FAVOUR OF GET_LANGUAGE_METADATA
    Get Python version and implementation """
    return {
        "Python Version": sys.version,
        "Python Implementation": platform.python_implementation()
    }




### Environment Metadata --------------------------------------------------

def get_environment_metadata(env_files) -> dict:
    """ Get metadata about environment management and managed packages """
    get_conda_metadata(env_files[environment_yml])
    
    raise NotImplementedError


def get_conda_metadata(env_file):
    """ Get whether conda is present and if so, packages in environment.yml """
    if os.environ.get("CONDA_DEFAULT_ENV"):
        conda_present, channels, dependencies = True, [], []
        
        if not env_file:
            # Attempt to locate environment.yml in current working directory
            path = os.path.join(os.getcwd(), "environment.yml")
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


def get_venv_metadata():
    # In active venv environment bool
    raise NotImplementedError


def get_docker_metadata():
    # Running in docker container bool
    raise NotImplementedError


def get_virtual_env_metadata():
    # Cloud instance detection bool
    raise NotImplementedError