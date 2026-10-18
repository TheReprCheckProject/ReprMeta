""" ReprMeta util.py 

Utility functions required for ReprMeta operation that are not either core 
functions or specific metadata-retrieval functions.

"""


def load_json(json_path) -> dict:
    """ Load ReprMeta-generated JSON from path into dict """
    raise NotImplementedError


def get_env_files(custom_file_paths) -> dict:
    """ Detect and return paths to environment files """
    raise NotImplementedError


def get_present_languages() -> set:
    """ Get (non-comprehensive) set of languages detected in project """
    raise NotImplementedError