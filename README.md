# PyArchery

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Servier Inspired](https://raw.githubusercontent.com/servierhub/.github/main/badges/inspired.svg)

**PyArchery** is a Python binding for the [Java Archery Framework](https://github.com/RomualdRousseau/Archery), enabling powerful semi-structured document processing directly from Python. It leverages [JPype](https://jpype.readthedocs.io/) to bridge Python and Java, providing seamless access to Archery's intelligent extraction, layout analysis, and tag classification capabilities.

## Description

In today's data-driven landscape, navigating the complexities of semi-structured documents poses a significant challenge. PyArchery brings the robust capabilities of the Archery framework to the Python ecosystem.

By leveraging innovative algorithms and machine learning techniques, Archery offers a solution that gives you control over the data extraction process with tweakable and repeatable settings. It automates the extraction process, saving time and minimizing errors, making it ideal for industries dealing with large volumes of documents.

Key features include:

- **Intelligent Extraction**: Automatically extract structured data from documents.
- **Layout Analysis**: Understand the physical layout of document elements.
- **Tag Classification**: Classify document tags using customizable styles (Snake case, Camel case, etc.).
- **Java Integration**: Direct access to the underlying Java Archery API for advanced usage.

## Getting Started

### Prerequisites

- **Java Development Kit (JDK)**: Version 21 or higher is required.
- **Python**: Version 3.11 or higher.

### Installation

Install PyArchery using pip:

```bash
pip install pyjarchery
```

### Quick Start

Here's a simple example of how to use PyArchery to open a document and extract data from tables:

```python
import pyarchery

# Path to your document
file_path = "path/to/your/document.pdf"

# Load the document with intelligent extraction hints
# This returns a DocumentWrapper
with pyarchery.load(
    file_path,
    hints=[pyarchery.INTELLI_EXTRACT, pyarchery.INTELLI_LAYOUT]
) as doc:
    # Access sheets using the pythonic wrapper property
    for sheet in doc.sheets:
        # Check if sheet has a table
        if sheet.table:
            table = sheet.table
            # Convert to python dictionary
            data = table.to_pydict()
            print(f"Extracted data from table: {data.keys()}")
```

## Documentation

For comprehensive documentation, tutorials, and API references, please visit:

- **PyArchery Documentation**: [https://romualdrousseau.github.io/PyArchery/](https://romualdrousseau.github.io/PyArchery/)
- **Java Archery Framework**: [https://github.com/RomualdRousseau/Archery](https://github.com/RomualdRousseau/Archery)

## Configuration

You can tune runtime behavior via environment variables:

- `PYARCHERY_MAVEN_URL` / `PYARCHERY_MAVEN_SNAPSHOT_URL`: Override Maven base URLs for downloading Java dependencies.
- `PYARCHERY_JARS_HOME`: Directory where downloaded JARs are cached (default is inside the package). Useful to share a cache across virtual environments or reduce wheel size by keeping jars out of the wheel.
- `PYARCHERY_SKIP_JVM_START`: Set to `1` to skip JVM startup (for dry runs or environments where Java is managed externally).
- `PYARCHERY_REQUIRE_CHECKSUMS`: Set to `1` to enforce checksum verification of downloaded JARs (fails if checksum file is missing or mismatched).
- `PYARCHERY_FETCH_ALL_NATIVE`: Set to `1` to download all native classifiers instead of filtering by the current platform.

### Wheel slimming

The default build excludes bundled JARs; on first use PyArchery downloads only the platform-matching artifacts. To avoid repeated downloads across projects or CI runs, set `PYARCHERY_JARS_HOME` to a shared cache directory. If you need a “fat” wheel that includes JARs, consider providing a separate distribution or optional extra that re-enables JAR bundling, while keeping the default wheel lightweight.

## Contribute

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Authors

- Romuald Rousseau, romualdrousseau@gmail.com
