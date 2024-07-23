#!/bin/bash

# ./init.sh --password ubuntu --reboot true
# Initialize variables
PASSWORD=""
REBOOT=""

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --password) PASSWORD="$2"; shift ;;
        --reboot) REBOOT="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Output the parsed values
echo "Password: $PASSWORD"

# if [ "$REBOOT" = "true" ]; then
#     echo "Reboot: $REBOOT"
# fi

sudo apt install ssh git connect-proxy python3-jinja2
ssh-keygen -t rsa -m PEM
ssh-copy-id localhost
pip install ansible-runner
# python ansible-python.py -p $PASSWORD
