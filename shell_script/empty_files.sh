
# Create a shell script that finds and lists all empty files in a directory.
#!/bin/bash

read -p "Enter directory: " directory


# Check if the directory exists
if [ ! -d "$directory" ]; then
    echo "Error: Directory '$directory' does not exist."
    exit 1
fi

# Find and list all empty files
empty_files=$(find "$directory" -type f -empty)

#"$variable":
# The variable you want to check.
# -z:
# Returns true if the variable is empty or unset

if [ -z "$empty_files" ]; then
    echo "No empty files found in the directory '$directory'."
else
    echo "Empty files in the directory '$directory':"
    echo "$empty_files"
fi