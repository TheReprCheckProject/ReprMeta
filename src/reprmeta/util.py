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


def get_present_languages(exts) -> set:
    """ Get (non-comprehensive) set of languages detected in project 
    
    Note: does not detect scripts without language-specific file extensions
    
    """
    # Load file extension - language mapping
    with open(Path("vendor/languages/languages.yml", "r")) as file:
        lang_data = yaml.safe_load(file)
        
    # Map extensions to languages
    mapping = dict()
    for lang in lang_data:
        for ext in lang_data[lang][extensions]:
            mapping[ext] = mapping.get(ext, set()).add(lang.lower())

    langs_found = {langs for ext, langs in mapping.items() if ext in exts}
    return langs_found


def rel_path(path: Path):
    """ Return relative path of path from project root (current working dir) """
    return path.relative_to(Path.cwd())
