""" ReprMeta metadata.py 

Dedicated automated metadata retrieval functions.

"""

from datetime import datetime
from importlib.metadata import version, PackageNotFoundError
import locale
import os
import platform
import subprocess
import sys

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

def get_hpc_metadata(exts) -> str | None:
    """ Get HPC job scheduler based on presence of HPC-specific env variable """
    hpc_env_vars = {
        "Slurm": "SLURM_JOB_ID",
        "PBS": "PBS_JOBID",
        "LSF": "LSB_JOBID",
        "SGE": "SGE_ROOT",
        "HTCondor": "CONDOR_JOBID",
        "AWS Batch": "AWS_BATCH_JOB_ID",
        "Google Cloud Batch": "GOOGLE_CLOUD_BATCH_JOB",
        "Azure Batch": "AZ_BATCH_JOB_ID",
    }

    for scheduler, env_var in hpc_env_vars.items():
        if os.environ.get(env_var):
            return scheduler
    return None


def get_os_metadata():
    """ Get operating system, release, and OS version """
    return {
        "OS": platform.system(),
        "OS Release": platform.release(),
        "OS Version": platform.version(),
    }    


def get_hardware_metadata():
    """ Get machine, architecture, number of cores, and processor name """
    return {
        "Machine": platform.machine(),
        "Architecture": platform.architecture()[0],
        "Number of Logical Cores": os.cpu_count(),
        "Processor": platform.processor()
    }


def get_regional_metadata():
    """ Get locale and encoding (tend to be region-specific) """
    return {
        "Locale": locale.getlocale()[0], 
        "Encoding": locale.getlocale()[1]
    }




### Language Metadata -----------------------------------------------------

def get_language_metadata(languages: set) -> dict:
    """ Get language version/s and other language-specific metadata """
    # Get python version and implementation metadata. Other language metadata
    # will be added to this dictionary.
    all_lang_metadata = get_python_metadata()
    
    # Define language metadata commands
    lang_commands = {
        "r": {"version": ["Rscript", "-e", "as.character(getRversion())"]},
        "julia": {"version": ["julia", "e", "print(VERSION)"]},
        "perl": {"version": ["perl", "-e", "print substr($^V,1)"]},
        "bash": {"version": ["bash", "--version"]},
        "ruby": {"version": ["ruby", "-e", "print RUBY_VERSION"]},
        "java": {"version": ["java", "-version"]},
        "go": {"version": ["go", "version"]},
        "rust": {"version": ["rustc", "--version"]},
        
        # Compiled languages. Do not include standard as this cannot reliably
        # be queried. The current standard does not necessarily equal the
        # standard used for building. Standard should be manually annotated.
        "c": {
            "clang_version": ["clang", "--version"],
            "gcc_version": ["gcc", "-dumpversion"]
        },
        "c++": {
            "clang_version": ["clang++", "--version"],
            "gcc_version": ["g++", "-dumpfullversion"]
        },

        # Workflow languages
        "nextflow": {"version": ["nextflow", "-version"]},
        "snakemake": {
            "version": [
                "python", "-c","import snakemake; print(snakemake.__version__)"
            ]
        }
    }
    
    # Execute language metadata commands and store results in dictionary
    for lang in languages:
        command_dict = lang_commands.get(lang, dict())
        
        # Execute each language-specific command. No commands are executed for
        # languages without at least one predefined language metadata command.
        lang_dict = dict()
        for cmd_type in command_dict:
            command = command_dict[cmd_type]
            
            # Execute the language-specific command and store result. If the
            # command fails and is not related to a compiled language, note 
            # this metadata command is unsupported 
            # by this version of ReprMeta instead of raising an error.
            try:
                lang_dict[cmd_type] = subprocess.run(
                    command,
                    capture_output=True, text=True, check=True
                ).stdout.strip()
            except:
                if lang != "c" and lang != "c++":
                    lang_dict[cmd_type] = "unsupported by ReprMeta " \
                        f"{get_reprmeta_version()}"
                else:
                    lang_dict[cmd_type] = None
        
        # Add language-specific metadata to the main languages dict. If the
        # language is unsupported by this version, add unsupported note instead.
        if lang_dict:
            all_lang_metadata[lang] = lang_dict
        else:
            all_lang_metadata[lang] = "unsupported by ReprMeta " \
                f"{get_reprmeta_version()}"
    
    return all_lang_metadata


def get_python_metadata():
    """ Get Python version and implementation """
    return { 
        "python": {
            "version": sys.version,
            "implementation": platform.python_implementation()
        }
    }




### Environment Metadata --------------------------------------------------

def get_environment_metadata(env_files: dict) -> dict:
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
                if isinstance(dependency, dict) and "pip" in dependency: 
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