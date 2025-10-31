#!/bin/bash
# Debug launcher for Bible Study Finder Backend (Linux/Mac)

echo "Starting Bible Study Finder API Debug Server..."
echo

# Set debug environment variables
export DEBUG=true
export ENVIRONMENT=development
export PYTHONPATH="$(pwd)"

echo "Debug Mode: ON"
echo "Environment: Development" 
echo "Working Directory: $(pwd)"
echo

# Try to run the debug server
python3 debug_server.py --mode fastapi

# If that fails, try simple mode
if [ $? -ne 0 ]; then
    echo
    echo "FastAPI failed, trying simple test server..."
    python3 debug_server.py --mode simple
fi
