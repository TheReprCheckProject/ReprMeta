# ReprMeta

![Python](https://img.shields.io/badge/language-python-green)
![License: CC-BY-NC-4.0](https://img.shields.io/badge/license-CC--BY--NC--4.0-lightgrey)
<!-- ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/TheReprCheckProject/ReprMeta -->)
<!-- ![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.XXXXXX-blue) -->
<!-- ![Bioconda](https://img.shields.io/conda/vn/bioconda/reprmeta) -->

A python package for embedding reproducibility metadata into notebooks, pipelines, and scientific workflows.

## About
ReprMeta lowers the barrier to reproducible research by automating a substantial portion of metadata annotation. It can display execution metadata directly inside Jupyter notebooks or export it to a structured JSON file. ReprMeta only reveals user‑specified paths and avoids exposing sensitive environment details. Where automatic detection is not possible nor appropriate, ReprMeta allows users to inject their own contextual metadata into exported files.


## Installation
```python
pip install reprmeta
```

## Usage Examples
Importing ReprMeta:
```python
import reprmeta
```
Rendering a ReprMeta Dictionary in a Jupyter Notebook:
```python
reprmeta.metadata()
```
Fetching a ReprMeta Metadata Dictionary:
```python
reprmeta.get_metadata() # Alias for reprmeta.metadata()
```
Printing ReprMeta Metadata to Console:
```python
reprmeta.print_metadata()
```
Exporting Metadata to JSON File:
```python
# The comments option allows the user to inject additional metadata that cannot be automatically retrieved by ReprMeta.
reprmeta.export_metadata(
    dest = "path/to/destination.json",
    comments = {"Author": "John Smith", "Dataset Version": "0.1.0"}
)
```

## Citation


## License
This tool is licensed under Creative Commons Attribution–NonCommercial 4.0 International (CC BY‑NC 4.0). 
Commercial use and patenting are prohibited. Academic use is permitted with citation.
