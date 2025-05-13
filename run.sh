#!/bin/bash

set -e

# Step 1: Create a virtual environment
python3 -m venv venv

# Step 2: Activate the virtual environment
source venv/bin/activate

# Step 3: Install the package (assuming setup.py is in the same directory)
python setup.py

# Step 4: Run the main script
python main.py
