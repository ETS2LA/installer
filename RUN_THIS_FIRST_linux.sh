#!/bin/bash

python --version 2>&1 | grep -q -E "Python 3\.(10|11)\."
if [ $? -ne 0 ]; then
    python3 --version 2>&1 | grep -q -E "Python 3\.(10|11)\."
    if [ $? -ne 0 ]; then
        echo "- Error: Incompatible Python version found"
        echo ""
        echo "Please install either Python 3.10 or 3.11."
        echo ""
        read -n1 -r -p "Press any key to continue..."
        exit
    else
        echo "- Error: Python is run with 'python3'"
        echo ""
        echo "You actually have the correct Python version installed but it's run with 'python3'. If you're on a Debian-based distro, you can install the package 'python-is-python3' to make 'python' point to 'python3'."
        echo ""
        read -n1 -r -p "Press any key to continue..."
        exit
    fi
fi


command -v npm >/dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "- Error: NPM not installed"
	echo "? Continuing will try and install Node automatically, CTRL+C to cancel"
	read -n1 -r -p "Press any key to continue..."
	python helpers/download_node_linux.py
	echo ""
	echo "Please restart the script to check if Node was installed correctly."
	echo "If it's not working then you can install it manually from https://nodejs.org/en"
	read -n1 -r -p "Press any key to continue..."
	exit
fi

command -v git >/dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "- Error: Git not installed"
	echo "? Continuing will try and install Git automatically, CTRL+C to cancel"
	read -n1 -r -p "Press any key to continue..."
	python helpers/download_git_linux.py
	echo ""
	echo "Please restart the script to check if Git was installed correctly."
	echo "If it's not working then you can install it manually from https://git-scm.com/downloads"
	read -n1 -r -p "Press any key to continue..."
	exit
fi

echo "All prerequisites are installed, you can now run the START file."
read -n1 -r -p "Press any key to continue..."
