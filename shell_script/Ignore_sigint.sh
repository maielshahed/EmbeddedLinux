



#How do you handle signals like Ctrl+C in a shell script?


#!/bin/bash

trap '' SIGINT  # Ignore SIGINT initially
echo "Ignoring SIGINT. Waiting for 10 seconds..."
sleep 10

trap - SIGINT  # Restore default SIGINT behavior
echo -e "\nSIGINT handling restored. Press Ctrl+C to terminate."

sleep 10

chmod +x Ignore_sigint.sh