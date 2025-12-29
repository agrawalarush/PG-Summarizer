#!/bin/bash
# Setup script for PostgreSQL Hackers Weekly Blog Generator

set -e

echo "Setting up PostgreSQL Hackers Weekly Blog Generator..."
echo

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "ERROR: Python 3 is required"; exit 1; }

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p blogs

# Make main script executable
chmod +x main.py

echo
echo "Setup complete!"
echo
echo "To run the blog generator:"
echo "  source venv/bin/activate  # if using virtual environment"
echo "  python3 main.py"
echo
echo "To set up weekly automation:"
echo "  See README.md for cron or systemd timer instructions"



