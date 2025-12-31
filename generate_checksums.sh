#!/bin/bash

OUTPUT_FILE="src/pyarchery/dependencies.sha256"
JAR_DIR="src/pyarchery.jars"

# Clear the output file if it exists
> "$OUTPUT_FILE"

# Iterate over each .jar file in the specified directory
for jar_file in "$JAR_DIR"/*.jar; do
    if [ -f "$jar_file" ]; then
        # Calculate SHA256 checksum and get the file name
        checksum=$(sha256sum "$jar_file" | awk '{print $1}')
        file_name=$(basename "$jar_file")
        
        # Append to the output file in the format checksum:file_name
        echo "${checksum}:${file_name}" >> "$OUTPUT_FILE"
    fi
done

echo "Generated SHA256 checksums in $OUTPUT_FILE"