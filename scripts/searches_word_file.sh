


#Create a script that searches for a specific word in a file and counts its occurrences.

#!/bin/bash
read -p "Enter filename: " filename
read -p "Enter a word to search for: " word
grep -w -n $word $filename
if [ $? -eq 1 ]; then
echo "Pattern did not match."
fi

# Check if the file exists
if [ ! -f "$filename" ]; then
    echo "Error: File '$filename' not found."
    exit 1
fi


# Count the occurrences of the word
count=$(grep -ow "$word" "$filename" | wc -l)

echo "The word '$word' appears $count times in the file '$filename'."