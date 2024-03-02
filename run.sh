#!/bin/bash

# Find the virtual environment activation script
VENV_ACTIVATE=$(find . -name "activate" | grep "/venv/bin/activate")

if [ -z "$VENV_ACTIVATE" ]; then
    echo "Virtual environment activation script not found. Update the script with the correct path."
    exit 1
fi

while true
do
    echo "Starting server at $(date)"
    
    # Activate virtual environment
    source $VENV_ACTIVATE
    
    # Run the server in the background
    nohup python3 main.py > server.log 2>&1 &
    SERVER_PID=$!
    echo "Server is running with PID $SERVER_PID"
    
    # Deactivate virtual environment
    deactivate

    # Sleep for a period of time (e.g., 1 hour)
    sleep 1h

    echo "Stopping server at $(date)"
    kill $SERVER_PID
    wait $SERVER_PID 2>/dev/null # Suppress "Terminated" message
done
