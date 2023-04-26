#!/bin/bash

# Script to run the daily_automated.py SNODAS Tools Python program from the cron scheduler.

# Set the DISPLAY variable needed for X windows:
# - needed to run TSTool
checkXWindowsDisplay() {
  if [ -z "${DISPLAY}" ]; then
    # DISPLAY environment variable is not set so set it:
    # - assume running X server and program on one computer

    # Setting the DISPLAY variable might not be needed.
    hostname=$(hostname)
    fullDisplay="${hostname}:10.0"
    echo "Setting DISPLAY=${fullDisplay} to work with X Windows server."
    export DISPLAY="${fullDisplay}"

    # This is EXTREMELY important.
    # Allows QT to run in headless mode by rendering to an offscreen buffer.
    # Without setting this environment variable,
    # daily_automated.py will error and will not run.
    export QT_QPA_PLATFORM="offscreen"
  else
    # DISPLAY already set
    echo "Using DISPLAY=${DISPLAY} for X Windows server."
  fi
}

# Attempt to change to the scripts folder, and exit this script if it does not exist.
cd /var/opt/snodas-tools/scripts || exit

# Check if X Windows DISPLAY variable is set.
checkXWindowsDisplay &> /tmp/snodas-info.log

# Run the automated script, and send both stdout and stderr to the given temp file.
python3 -m snodas.app.daily_automated.py &>> /tmp/snodas-info.log
