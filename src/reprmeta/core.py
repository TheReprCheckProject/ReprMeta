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

### Get metadata functions ------------------------------------------------



### Core functions --------------------------------------------------------

def get_metadata() -> dict:
    """ Create dict containing comprehensive reproducibility metadata """
    raise NotImplementedError


def metadata() -> dict:
    """ Alias for get_metadata() """
    return get_metadata()


def print_metadata():
    """ Pretty-print metadata to console """
    raise NotImplementedError


def export_metadata(dest="", filename="reprmeta"):
    """ Write metadata to .json file at dest file/directory """
    raise NotImplementedError