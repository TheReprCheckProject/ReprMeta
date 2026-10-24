""" ReprMeta metadata.py 

Automated metadata retrieval functions.

"""

from datetime import datetime
from importlib.metadata import version, PackageNotFoundError
import locale
import os
import platform
import shutil
import subprocess
import sys

import yaml

import util


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
    unsupported_msg = f"unsupported by ReprMeta {get_reprmeta_version()}"
    
    # Get python version and implementation metadata. Other language metadata
    # will be added to this dictionary.
    all_lang_metadata = get_python_metadata()
        
    # Execute language metadata commands and store results in dictionary
    lang_commands = get_lang_commands()    
    for lang in languages:
        command_dict = lang_commands.get(lang, dict())
        
        # Execute each language-specific command. No commands are executed for
        # languages without at least one predefined language metadata command.
        lang_dict = dict()
        for cmd_type in command_dict:
            command = command_dict[cmd_type]
            
            # If the command fails and is not related to a compiled language, 
            # use unsupported_msg instead of raising an error.
            try:
                lang_dict[cmd_type] = subprocess.run(
                    command, capture_output=True, text=True, check=True
                ).stdout.strip()
            except:
                if lang != "c" and lang != "c++":
                    lang_dict[cmd_type] = unsupported_msg
                else:
                    lang_dict[cmd_type] = None
        
        # Add supported language-specific metadata to the main languages dict.
        if lang_dict:
            all_lang_metadata[lang] = lang_dict
        else:
            all_lang_metadata[lang] = unsupported_msg
    
    return all_lang_metadata


def get_python_metadata():
    """ Get Python version and implementation """
    return { 
        "python": {
            "version": sys.version,
            "implementation": platform.python_implementation()
        }
    }


def get_lang_commands():
    """ Define and return language metadata commands """
    return {
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




### Environment Metadata --------------------------------------------------

def get_environment_metadata(env_files: dict) -> dict:
    """ Get metadata about environment management and managed packages """
    return {
        "docker": get_docker_metadata(
            env_files["dockerfile"], env_files["docker_compose_yml"]
        ),
        "conda": get_conda_metadata(env_files["environment_yml"]),
        "renv": get_renv_metadata(env_files["renv_lock"]) # TODO        
    }


def get_docker_metadata(dockerfile, docker_compose_yml):
    """ Get basic docker metadata from dockerfile and/or docker compose """
    if not dockerfile and not docker_compose_yml: return None
    d_dict = dict() # docker metadata dictionary
    
    # Record relative path/s to docker-related files
    if dockerfile: d_dict.update({"dockerfile": util.rel_path(dockerfile)})
    if docker_compose_yml:
        d_dict.update({"docker_compose_yml": util.rel_path(docker_compose_yml)})
    
    # Find docker executable and record version if docker executable is present
    docker_exe = shutil.which("docker")
    d_dict.update({"docker_present": bool(docker_exe)})
    if docker_exe:
        d_dict.update(
            {"docker_version": subprocess.run(
                [docker_exe, "--version"],
                capture_output=True, text=True
            ).stdout.strip()}
        )
    
    # Record images specified in Dockerfile
    if d_dict.get(dockerfile, None):
        dockerfile_images = []        
        with open(dockerfile, "r") as f:
            for line in f:
                line = line.strip()
                if not line.upper().startswith("FROM "): continue
                tokens = line.split()
                # FROM image / FROM image AS stage
                if len(tokens) >= 2: images.append(tokens[1])
        d_dict.update({"dockerfile_images": dockerfile_images})
    
    # Record images specified in docker_compose.yml
    if d_dict.get(docker_compose_yml, None):
        compose_images = []
        with open(docker_compose_yml, "r") as f:
            compose = yaml.safe_load(f)
        for service in compose.get("services", {}).values():
            image = service.get("image", None)
            if image: compose_images.append(image)
        d_dict.update({"docker_compose_images": compose_images})
    
    return d_dict


def get_conda_metadata(environment_yml):
    """ Get channels and packages specified in environment.yml """
    if not environment_yml: return None
    conda_dict["conda_present"] = bool(os.environ.get("CONDA_DEFAULT_ENV"))
    conda_dict = {"environment_yml": environment_yml.relative_to(Path.cwd())}    
    
    # Parse channels and dependencies in environment.yml-like file
    channels, dependencies = [], []
    with open(environment_yml, "r") as file:
        data = yaml.safe_load(file)
    channels = sorted(data["channels"])
    raw_deps = data["dependencies"]
    
    # Record conda and pip dependencies in environment.yml-like file
    for dep in raw_deps:
        if isinstance(dep, dict) and "pip" in dep: # deal with pip dependencies
            dependencies.extend(dep["pip"])
        else:
            dependencies.append(dep)
    dependencies = sorted(dependencies)

    # Return conda metadata
    conda_dict.update({"channels": channels, "dependencies": dependencies})
    return conda_dict


def get_renv_metadata(renv_lock):
    raise NotImplementedError


def get_venv_metadata():
    # In active venv environment bool
    raise NotImplementedError


def get_virtual_env_metadata():
    # Cloud instance detection bool
    raise NotImplementedError