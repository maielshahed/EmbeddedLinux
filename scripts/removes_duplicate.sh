
#. Create a script that checks for and removes duplicate lines in a text file
#!/bin/bash


read -p "Enter filename: " filename

# Check if the file exists
if [ ! -f "$filename" ]; then
    echo "Error: File '$filename' not found."
    exit 1
fi

# Create a backup of the original file
backup_file="${filename}.bak"
cp "$filename" "$backup_file"

# Remove duplicate lines and save the result back to the file
sort -u "$filename" -o "$filename"

echo "Duplicate lines removed. A backup of the original file is saved as '$backup_file'."

chmod +x remove_duplicates.sh
#bash./remove_duplicates.sh