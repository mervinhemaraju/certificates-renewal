#!/bin/bash

# Create a variable for the main directory
WORKING_DIR="/home/th3pl4gu3/workspace/certificates-renewal/scripts/cert_sync"

# Activate the venvironment
source $WORKING_DIR/.venv/bin/activate

# Source the secrets file
source $WORKING_DIR/secrets.env

# Run the script
$WORKING_DIR/.venv/bin/python $WORKING_DIR/runner.py

# Deactivate the virtual environment
deactivate