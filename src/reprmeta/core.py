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
import os
import platform
import subprocess
import importlib.metadata
from datetime import datetime


### Get metadata functions ------------------------------------------------


#def get_python_metadata():
    #return {
        #"python_version": platform.python_version(),
        #"python_executable": sys.executable,
        #"implementation": platform.python_implementation(),
    #}



#def get_timestamp():
    #return {
        #"timestamp": datetime.now().isoformat()
    #}


#def get_installed_packages():
    #"""Returns installed packages using importlib.metadata (Python ≥3.8)."""
    #packages = {}
    #for dist in importlib.metadata.distributions():
        #name = dist.metadata["Name"]
        #version = dist.version
        #packages[name] = version
    #return {"packages": packages}


#def get_conda_env():
    #"""Returns conda environment name and prefix if available."""
    #conda_prefix = os.environ.get("CONDA_PREFIX")
    #conda_default_env = os.environ.get("CONDA_DEFAULT_ENV")

    #return {
        #"conda_prefix": conda_prefix,
        #"conda_env": conda_default_env,
    #}




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
        )
        
        remote_url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"]
        ).decode().strip()

        return {"git_commit": commit, "git_branch": branch, 
                "git_status": status, "git_remote_url": remote_url}

    except Exception:
        return {}


def get_hardware_metadata():
    """ Get machine, architecture, number of cores, and processor name """
    return {"machine": platform.machine(),
            "architecture": platform.architecture()[0],
            "num_cores": os.cpu_count(),
            "processor": platform.processor()}


def get_os_metadata():
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
    }    


def get_python_metadata():
    raise NotImplementedError


def get_conda_metadata():
    raise NotImplementedError


def get_misc_metadata():
    raise NotImplementedError


def get_jupyter_metadata():
    raise NotImplementedError


def get_hpc_metadata():
    raise NotImplementedError


### Core functions --------------------------------------------------------

def get_metadata() -> dict:
    """ Create dict containing comprehensive reproducibility metadata """
    metadata = {}
    return metadata


def metadata() -> dict:
    """ Alias for get_metadata() """
    return get_metadata()


def print_metadata():
    """ Pretty-print metadata to console """
    metadata = get_metadata()
    for key, value in metadata.items():
        print(f"{key}: {value}")


def export_metadata(dest="", filename="reprmeta"):
    """ Write metadata to .json file at dest file/directory """
    raise NotImplementedError