#!/bin/bash

# Setup script for Android Management API Server

echo "Setting up Android Management API Server..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your Google Cloud credentials"
echo "2. Download your service account key and place it in the path specified in .env"
echo "3. Run: python app.py"
