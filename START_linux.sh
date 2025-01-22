#!/bin/bash

if [ ! -f "checked.txt" ]; then
  echo "You didnt run the RUN_THIS_FIRST_linux.sh ! Please exit and run the RUN_THIS_FIRST_linux.sh !"
  exit 1
fi

if [ ! -d "code" ]; then
    echo "- Error: code folder not found"
    echo ""
    echo "Please make sure the file is being run from the correct directory."
    echo ""
    read -n1 -r -p "Press any key to continue..."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    echo "Virtual environment created"
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Checking requirements..."
pip install -q -r code/requirements.txt
echo "+ Done"

echo "Running the installer / app..."
sleep 1

source venv/bin/activate
sudo -E venv/bin/python code/installer.py

