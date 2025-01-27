
#Write a shell script that converts all filenames in a directory to lowercase.
#!/bin/bash
read -p "Enter directory: " directory



# Check if the directory exists
if [ ! -d "$directory" ]; then
    echo "Error: Directory '$directory' does not exist."
    exit 1
fi

# Iterate through all files in the directory
for file in "$directory"/*; do
    # Skip if it's not a regular file
    [ -f "$file" ] || continue

    # Get the directory, base name, and lowercase name
    dir=$(dirname "$file")
    base=$(basename "$file")
    lowercase=$(echo "$base" | tr '[:upper:]' '[:lower:]')

    # Rename the file only if the name is different
    if [ "$base" != "$lowercase" ]; then
        mv "$file" "$dir/$lowercase"
        echo "Renamed: $file -> $dir/$lowercase"
    fi
done

echo "All filenames in '$directory' have been converted to lowercase."