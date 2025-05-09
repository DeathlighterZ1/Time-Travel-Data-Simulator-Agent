#!/bin/bash

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Authenticate with Earth Engine (if needed)
echo "You may need to authenticate with Earth Engine using:"
echo "earthengine authenticate"

echo "Setup complete! Run the simulator with:"
echo "python time_travel_simulator.py"