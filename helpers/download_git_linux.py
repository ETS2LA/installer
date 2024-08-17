import os

#Detect Distro 

print("Detecting distro...")

try:
    distro = os.popen("lsb_release -si").read().lower().strip()
except KeyError:
    distro = "unknown"

print("Detected distro: " + distro)
if distro != "unknown":
    checkinput = ""
    while checkinput != "y" and checkinput != "n":
        checkinput = input("Is this correct? (y/n) ")

    if checkinput == "y":
        pass
    elif checkinput == "n":
        print("That's not very good. Please pay close attention to the next prompt.")

if distro == "linuxmint" or distro == "ubuntu" or distro == "debian":
    checkinput = ""
    while checkinput != "y" and checkinput != "n":
        checkinput = input("Would you like to install Git via apt? (y/n) ")
    if checkinput == "y":
        print("Installing Git via apt...")
        os.system("sudo apt update")
        os.system("sudo apt install git -y")
    elif checkinput == "n":
        print("Please install Git manually and try again.")

if distro == "arch" or distro == "manjaro":
    checkinput = ""
    while checkinput != "y" and checkinput != "n":
        checkinput = input("Would you like to install Git via pacman? (y/n) ")
    if checkinput == "y":
        print("Installing Git via pacman...")
        os.system("sudo pacman -S git")
    elif checkinput == "n":
        print("Please install Git manually and try again.")

if distro == "unknown":
    print("Distro not detected. Please install Git manually and try again.")

if distro != "unknown" and distro != "linuxmint" and distro != "ubuntu" and distro != "debian" and distro != "arch" and distro != "manjaro":
    print("Your distro is not supported. Please install Git manually and try again.")
    quit()

#Check if git is installed

print("Checking if Git is installed...")

try:
    os.system("git --version")
    print("Git is installed!")
except:
    print("It seems that Git failed to install. Please install Git manually and try again.")