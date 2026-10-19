""" ReprMeta util.py 

Utility functions required for ReprMeta operation that are not either core 
functions or specific metadata-retrieval functions.

"""

from pathlib import Path




def load_json(json_path) -> dict:
    """ Load ReprMeta-generated JSON from path into dict """
    raise NotImplementedError


def get_env_files(custom_file_paths) -> dict:
    """ Detect and return paths to environment files 
    
    Parse through root directory and specified custom file paths to detect
    and validate existence of environment management files, then report paths
    to existing environment file paths.
    
    """
    # Parse path strings into Paths
    custom_parsed = {key: Path(val) for key, val in custom_file_paths.items()}
       
    # Define standard/default locations for environment files
    paths = {
        "environment_yml": [Path("environment.yml"), Path("environment.yaml")],
        "renv_lock": [Path("renv.lock")],
        "dockerfile": [Path("Dockerfile")],
        "docker_compose_yml": [Path("docker_compose.yml")],
    }
    
    # Update default paths with custom specified environment file paths
    paths.update(custom_parsed)
    
    # Replace non-existent paths with None
    existing_paths = dict()
    for key, val in paths.items():
        for path in val:
            if path.exists():
                existing_paths[key] = path
                break

    return existing_paths


def get_project_exts() -> set:
    """ Return set of all file extensions found in project """
    return {f.suffix for f in Path('.').rglob('*') if f.is_file()}


def get_present_languages(exts) -> list:
    """ Get (non-comprehensive) set of languages detected in project """
    lang_exts = {
        ".py": "Python", ".R": "R"
    }
    langs_found = [lang for ext, lang in lang_exts.items() if ext in exts]
    return langs_found