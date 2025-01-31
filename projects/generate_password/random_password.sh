#!/bin/bash

#!/bin/bash

# Define password length (adjust as needed)
password_length=16

# Function to generate a random password
generate_password() {
    password=""
    
    
    while [[ ${#password} -lt $password_length ]]; do
        # Generate a random character
        new_char=$(< /dev/urandom tr -dc 'A-Za-z' | head -c 1)

        # Check if the new character is the same as the last one
        if [[ ${#password} -gt 0 && "$new_char" == "${password: -1}" ]]; then
            continue  # Skip if the character is the same as the last one
        fi

        # Append the new character to the password
        password+="$new_char"
    done
}

# Generate the password
generate_password

# Output the password to a file (password.txt)
#echo "Generated password: $password" > password.txt


#overwriting any existing content in the file. If you want to append instead, use >>
echo "Generated password: $password" >> password.txt


# Optionally, print it to the terminal as well
echo "Generated password: $password"





chmod +x random_password.sh

