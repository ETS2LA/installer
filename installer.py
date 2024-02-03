"""

This file is responsible for making sure all the app's requirements are properly installed, before even trying to launch the python installer.

This file will also be packaged as an exe file, since most people don't even know what .bat files are :)

"""
BYPASS_CHECKS = False
DEFAULT_INSTALL_LOCATION = "C:\\LaneAssist"

import os
import sys
import subprocess

try: 
    import webbrowser
except: 
    os.system("pip install webbrowser")
    import webbrowser

# Parse the command line arguments
if len(sys.argv) > 1:
    if sys.argv[1] == "--bypass":
        BYPASS_CHECKS = True
        

def PrintRed(text):
    """
    Print text in red
    """
    print("\033[91m {}\033[00m".format(text))

def CheckForWinget():
    """
    Check if winget is installed on the system
    """
    try:
        subprocess.run(["winget", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def InstallWinget():
    """
    Install winget on the system
    """
    print("Opening winget install page...")
    subprocess.run(["start", "ms-windows-store://pdp?launch=true&mode=mini&hl=en-gb&gl=us&productid=9NBLGGH4NNS1"])
    from tkinter import messagebox
    messagebox.showinfo("Winget Installer", "Winget is not installed on your system. We have opened the installation page for you. Please install it and run this installer again.")
    exit()
    
def CheckForPython():
    """
    Check if python is installed on the system
    """
    try:
        version = subprocess.run(["python", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check that the version is 3.11.x
        if version.stdout.decode("utf-8").split(" ")[1].split(".")[0] == "3" and version.stdout.decode("utf-8").split(" ")[1].split(".")[1] == "11":
            return True
        else:
            return False
    except:
        return False
    
def InstallPython():
    """
    Install python on the system
    """
    try:
        subprocess.run(["winget", "install", "Python.Python.3.11"])
    except:
        PrintRed("Failed to install python. Please install it manually.")
        from tkinter import messagebox
        webbrowser.open("https://wiki.tumppi066.fi/tutorials/installing-the-correct-python-version")
        messagebox.showinfo("Python Installer", "Python 3.11.x is not installed on your system. Please uninstall all your previous versions, and install 3.11.x manually. Then run this installer again.")
        exit()
       
def CheckGit():
    """
    Check if git is installed on the system
    """
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def InstallGit():
    """
    Install git on the system
    """
    try:
        subprocess.run(["winget", "install", "Git.Git"])
    except:
        PrintRed("Failed to install git. Please install it manually.")
        from tkinter import messagebox
        messagebox.showinfo("Git Installer", "Failed to install git automatically, please download it from the website we will open after closing this window. Then run this installer again.")
        webbrowser.open("https://git-scm.com/download/win")
        exit()
       
def ColorTitleBar(root):
    # Change the titlebar color
    from ctypes import windll, c_int, byref, sizeof
    HWND = windll.user32.GetParent(root.winfo_id())
    returnCode = windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(0x1c1c1c)), sizeof(c_int))
       

def AskForPath():
    from tkinter import filedialog
    return filedialog.askdirectory()

def OpenFolderAndCloseApp(path):
    os.system("start " + path)
    sys.exit()
   
def Install(path, mirror):
    global installButton
    global root

    from tkinter import messagebox
    messagebox.showinfo("Installation", "The installation will now begin. The app will be unresponsive during installation. Please wait until the installation is complete.")
    if mirror == "Github":
        installButton.config(text="Cloning from Github...")
        root.update()
        os.system("git clone -b installer --single-branch https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist.git " + path)
        installButton.config(text="Open folder (open the menu.bat file in there)")
        installButton.config(command=lambda: OpenFolderAndCloseApp(path))
        installButton.config(style="Accent.TButton")
        messagebox.showinfo("Installation", "The installation is complete.")
    if mirror == "Sourceforge":
        installButton.config(text="Cloning from Sourceforge...")
        root.update()
        os.system("git clone -b installer --single-branch https://git.code.sf.net/p/eurotrucksimulator2-laneassist/code " + path)
        installButton.config(text="Open folder (open the menu.bat file in there)")
        installButton.config(command=lambda: OpenFolderAndCloseApp(path))
        installButton.config(style="Accent.TButton")
        messagebox.showinfo("Installation", "The installation is complete.")
   
        
if not BYPASS_CHECKS:
    # Check and install winget
    print("Checking for winget...")
    if not CheckForWinget():
        InstallWinget()
    print("> Winget is installed on your system.")

    print("")

    # Check and install python
    print("Checking for python...")
    if not CheckForPython():
        InstallPython()
        print("> Python 3.11.x is installed on your system.")
        # Check if it's the default
        if not CheckForPython():
            PrintRed("> Python 3.11.x is not the default python version on your system. Please uninstall all your previous versions. Then run this installer again.")
            from tkinter import messagebox
            webbrowser.open("https://wiki.tumppi066.fi/tutorials/installing-the-correct-python-version")
            messagebox.showinfo("Python Installer", "Python 3.11.x is not the default python version on your system. Please uninstall all your previous versions. Then run this installer again.")
            exit()
    else:
        print("> Python 3.11.x is installed on your system.")
            
    print("")
            
    print("Checking for git...")
    if not CheckGit():
        InstallGit()
    else:
        print("> Git is installed on your system.")
        

from tkinter import ttk
import tkinter as tk

try: 
    import sv_ttk
except: 
    os.system("pip install sv-ttk")
    import sv_ttk



# Create the main window
root = tk.Tk()
root.title("ETS2LA Installer")
root.geometry("400x280")
root.resizable(False, False)

# Try and color the title bar (windows 11 only)
root.update()
ColorTitleBar(root)

# Create the main frame
frame = ttk.Labelframe(root, text="Installer", width=400, height=300)
frame.grid_propagate(False)
frame.pack_propagate(False)
frame.pack(padx=10, pady=10)

# This is used to check if the path is empty or not
def ChangePath(path):
    global pathVar
    global warningLabel
    """
    Change the install location
    """
    pathVar.set(path)
    # Check if the path is empty
    if os.path.exists(path):
        if os.listdir(path):
            warningLabel.config(text="Error: The install location is not empty.")
            warningLabel.config(foreground="red")
            installButton.config(state="disabled")
        else:
            warningLabel.config(text="")
            installButton.config(state="normal")
    else:
        warningLabel.config(text="")
        installButton.config(state="normal")
        
    # Check if the path has spaces
    if " " in path:
        warningLabel.config(text="Error: The install location contains spaces.")
        warningLabel.config(foreground="red")
        installButton.config(state="disabled")
        
    root.update()

# Create the current path input box
pathVar = tk.StringVar()
currentPathLabel = ttk.Entry(frame, width=40, textvariable=pathVar, validatecommand=lambda: ChangePath(pathVar.get()), validate="all")
currentPathLabel.pack(pady=10)
currentPathLabel.bind("<Return>", lambda e: ChangePath(pathVar.get()))


# Create the change path button
changePathButton = ttk.Button(frame, text="Change install location", command=lambda: ChangePath(AskForPath()), width=39)
changePathButton.pack(pady=0)

# Create a warning for a path not empty
warningLabel = ttk.Label(frame, text="", foreground="yellow")
warningLabel.pack(pady=5)

# Create the mirror selector
mirrorVar = tk.StringVar()
mirrorVar.set("Github")
mirrorLabel = ttk.Label(frame, text="Select a mirror:")
mirrorLabel.pack(pady=5)
mirrorSelector = ttk.Combobox(frame, textvariable=mirrorVar, values=["Github", "Sourceforge"], width=36)
mirrorSelector.pack(pady=5)

# Create the install button
installButton = ttk.Button(frame, text="Install", command=lambda: Install(pathVar.get(), mirrorVar.get()), width=39)
installButton.pack(pady=5)

ChangePath(DEFAULT_INSTALL_LOCATION)
sv_ttk.set_theme("dark")
root.mainloop()