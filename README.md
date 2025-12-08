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

## Contribute

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Authors

- Romuald Rousseau, romualdrousseau@gmail.com
