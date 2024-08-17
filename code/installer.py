from rich.console import Console
import psutil
import shutil
import rich
import time
import sys
import os

console = Console()

# region Helpers
def bg(text, end="\n"):
    console.print("" + text + "", end=end, style="dim")
def fg(text, end="\n"):
    console.print("" + text + "", end=end)
def warn(text, end="\n"):
    console.print("[yellow]" + text + "[/yellow]", end=end)
def err(text, end="\n"):
    console.print("[red]" + text + "[/red]", end=end)
    if console.input("[red]┣ Continue? (Y/n)[/red] ") == "n": sys.exit(1)
def nl():
    console.print()
def replace_input(text, default=None):
    defaultText = text + default if default else ""
    first = True
    response = None
    while response not in ["y", "n", "", "Y", "N"]:
        if not first:
            sys.stdout.write("\033[F") # Move cursor up
            sys.stdout.write("\033[K")
        response = console.input(text)
        first = False
    if response == "": 
        sys.stdout.write("\033[F") # Move cursor up
        sys.stdout.write("\033[K")
        console.print(defaultText)
        return default
    return response
def wait(prefix, seconds, type = "line"):
    start = time.time()
    while time.time() - start < seconds:
        if type == "line":
            for c in ['|', '/', '-', '\\']:
                print(f'\r{prefix}Please wait... ' + c, end="")
                time.sleep(0.1)
        elif type == "block":
            for c in ['█', '▉', '▊', '▋', '▌', '▍', '▎', '▏']:
                print(f'\r{prefix}Please wait... ' + c, end="")
                time.sleep(0.1)
    print(f'\r{prefix}Please wait... Done.')
def start_app():
    if LINUX:
        os.chdir(DIR + "/app")
        os.system("python main.py")
    else:
        os.chdir(DIR + "\\app")
        os.system("python main.py")
# endregion

# region Variables

DIR =  sys.path[0]
VER = sys.version.split(" ")[0]
NODE_VER = os.popen("node -v").read().strip()
RAM = psutil.virtual_memory().total / 1024 / 1024 / 1024
CORES = psutil.cpu_count()
SPACE = psutil.disk_usage(DIR).free / 1024 / 1024 / 1024
GITHUB_URL = "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist.git"
SOURCEFORGE_URL = "https://tumppi066@git.code.sf.net/p/eurotrucksimulator2-laneassist/code"
LINUX = os.path.exists("/etc/os-release")
if LINUX:
    CLONED = os.path.exists(DIR + "/app")
else:
    CLONED = os.path.exists(DIR + "\\app")

# endregion

# region Stats

bg("┏ Hi, I'm the installer!")

bg("┣ I'm running in [bold]" + DIR + "[/bold]")
bg("┣ Python version: [cyan][bold]" + VER + "[/cyan][/bold]")
bg("┣ Node version: [cyan][bold]" + NODE_VER + "[/cyan][/bold]")

bg("┣ RAM: " + str(round(RAM, 1)) + " GB", end=" > ")
if RAM < 8: err("You have less than 8 GB of RAM. This may cause problems.")
elif RAM < 12: warn("You have less than 12 GB of RAM. It should be fine if you don't use chrome.")
else: bg("[bold]OK[/bold]")

bg("┣ Disk: " + str(round(SPACE, 1)) + " GB", end=" > ")
if SPACE < 2: err("You have less than 2 GB of free space. Please make more space!")
elif SPACE < 4: warn("[dim]You have less than 4 GB of free space. It should be fine if you don't install CUDA.[/dim]")
else: bg("[bold]OK[/bold]")

bg("┗ Cores: " + str(CORES), end=" > ")
if CORES < 4: err("You have less than 4 CPU cores. This may cause problems as the app is very much multi-threaded.")
elif CORES < 6: warn("You have less than 6 CPU cores. You should be fine... I think.")
else: bg("[bold]OK[/bold]")

# endregion

# region Installed check

nl()

bg("┏ Checking if the app is already cloned...")
bg("┗ " + ("It is - starting the app." if CLONED else "It's not - starting the install now."))

nl()

if CLONED:
    start_time = time.time()
    try:
        start_app()
        warn("\n[dim]┏ ETS2LA has been closed.[/dim]")
        warn("[dim]┗ You can check the logs above for information or errors and warnings.[/dim]")
        console.input("[dim]Press enter to exit [/dim]")
        sys.exit(0)
    except Exception as e:
        if time.time() - start_time < 5:
            err("┏ Something went wrong when starting.")
            fg("[red]┗ Removing the app and starting the install now.[/red]")
            try:
                shutil.rmtree(DIR + "\\app")
            except:
                err("\n┏ Couldn't remove the app folder. Please delete [code][bold]" + DIR + "\\app[/bold][/code] manually and restart the installer.")
                sys.exit(1)
        else:
            warn("\n[dim]┏ ETS2LA has been closed.[/dim]")
            warn("[dim]┗ You can check the logs above for information or errors and warnings.[/dim]")
            console.input("[dim]Press enter to exit [/dim]")
            sys.exit(0)
    
# endregion

# region Install questions

fg("┏ Let's ask some questions to get you started.")
CAN_ACCESS_GITHUB = replace_input("┣ 1 - Can you access [link https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist][blue][bold]GitHub[/bold][/blue][/link https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist] in your [i]country[/i]? (Y/n) > ", default="y") == "y"
HAS_NVIDIA = replace_input("┣ 2 - Do you have an [bold][green]NVIDIA[/green][/bold] GPU? (y/N) > ", default="n") == "y"
CUDA = False
if HAS_NVIDIA: CUDA = replace_input("┣ 3 - [bold][green]NVIDIA[/green][/bold] version for better performance? It requires [yellow]2gb[/yellow] more space. (Y/n) > ", default="y") == "y"
if replace_input("┣ [bold]OK[/bold] - ETS2LA will be installed to [bold]" + DIR + "\\app[/bold]. Continue? (Y/n) > ", default="y") == "n": sys.exit(1)
wait("┗ ", 2)

# endregion

# region Install

bg("\n┏ Starting install...")
bg(f"┗ Cloning from {'[yellow][bold]sourceforge[/bold][/yellow]' if not CAN_ACCESS_GITHUB else '[blue][bold]GitHub[/bold][/blue]'}...\n")

if not CAN_ACCESS_GITHUB:
    if LINUX:
        os.system(f"git clone {SOURCEFORGE_URL} {DIR}/app")
    else:
        os.system(f"git clone {SOURCEFORGE_URL} {DIR}\\app")
else:
    if LINUX:
        os.system(f"git clone {GITHUB_URL} {DIR}/app")
    else:
        os.system(f"git clone {GITHUB_URL} {DIR}\\app")
    
# Switch to the rewrite branch
if LINUX:
    os.system(f"cd {DIR}/app && git checkout rewrite")
else:
    os.system(f"cd {DIR}\\app && git checkout rewrite")
    
bg("\n┏ Git done, checking...")

if LINUX:
    if "requirements.txt" not in os.listdir(DIR + "/app"):
        err("┗ Something went wrong. The app wasn't cloned properly.")
        input("Press enter to exit.")
else:
    if "requirements.txt" not in os.listdir(DIR + "\\app"):
        err("┗ Something went wrong. The app wasn't cloned properly.")
        input("Press enter to exit.")

bg("┣ Cloned successfully, continuing...")
bg("┗ Installing python dependencies...\n")

if LINUX:
    with open(f"{DIR}/app/requirements.txt", "r+") as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if "pywin32" not in line:
                f.write(line)
        f.truncate()
    os.system(f"pip install -r {DIR}/app/requirements.txt")
else:
    os.system(f"pip install -r {DIR}\\app\\requirements.txt")

bg("\n┏ Dependencies done, continuing...")
bg("┗ Setting up node...\n")

if LINUX:
    os.system(f"cd {DIR}/app/frontend && npm install")
else:
    os.system(f"cd {DIR}\\app\\frontend && npm install")

#Install spesfic deps for linux

if LINUX:
    bg("\nInstalling spesific dependencies for linux...")

    os.system("pip3 install pyqt5 pyqtwebengine")
    os.system("pip3 install pywebview")
    os.system("pip3 install pywebview[qt]")

    #Make app folder a user folder
    bg("\nMaking app folder a user folder...")

    os.system(f"sudo chmod -R 777 {DIR}/app")

    #Check if tinkery is installed

    bg("\nChecking if tinker is installed...")


    try:
        import tkinter as tk
        bg("┏ Tinker is installed")
        bg("┗ Continuing...")
    except:
        bg("┏ Tinker is not installed")
        bg("┗ Installing...")

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
                checkinput = input("Would you like to install tkinter via apt? (y/n) ")
            if checkinput == "y":
                print("Installing tkinter via apt...")
                os.system("sudo apt update")
                os.system("sudo apt install python3-tk -y")
            elif checkinput == "n":
                print("Please install tkinter manually and try again.")

        if distro == "arch" or distro == "manjaro":
            checkinput = ""
            while checkinput != "y" and checkinput != "n":
                checkinput = input("Would you like to install tkinter via pacman? (y/n) ")
            if checkinput == "y":
                print("Installing tkinter via pacman...")
                os.system("sudo pacman -S tk")
            elif checkinput == "n":
                print("Please install tkinter manually and try again.")

        if distro == "unknown":
            print("Distro not detected. Please install tkinter manually and try again.")

        if distro != "unknown" and distro != "linuxmint" and distro != "ubuntu" and distro != "debian" and distro != "arch" and distro != "manjaro":
            print("Your distro is not supported. Please install tkinter manually and try again.")
            quit()

        #Check if tkinter is installed

        print("Checking if tkinter is installed...")

        try:
            import tkinter as tk
            print("Tkinter is installed!")
        except:
            print("It seems that tkinter failed to install. Please install tkinter manually and try again.")

    
# endregion

# region Install Dlls
if LINUX:
    bg("\n┏ Installing DLLs...")
    bg("┗ I don't know what to write here so and most people don't even read this so..................\n")

    #Check default debian folder for euro truck simulator 2
    if os.path.exists("/home/" + os.getlogin() + "/.steam/debian-installation/steamapps/common/Euro Truck Simulator 2/bin/linux_x64"):
        gamefolder = "/home/" + os.getlogin() + "/.steam/debian-installation/steamapps/common/Euro Truck Simulator 2/bin/linux_x64"
    else:
        fg("Failed to find Euro Truck Simulator folder. Please open steam and copy the game path and paste it below. or if the game is not installed leave blank and press enter")
        gamefolder = input()
        gamefolder = gamefolder.replace(" ", "")

    if gamefolder != "":

        if os.path.exists(gamefolder):
            if not os.path.exists(gamefolder + "/plugins"):
                folder = os.path.join(gamefolder, "plugins")
                os.system("mkdir -p \"" + folder + "\"")
            
            #Copy dlls
            try:
                os.system("cp -r ../helpers/dlls/Linux/* \"" + folder + "\"")
            except:
                print("Failed to copy dlls. Please copy them manually and try again.")

    if os.path.exists("/home/" + os.getlogin() + "/.steam/debian-installation/steamapps/common/American Truck Simulator/bin/linux_x64"):
        gamefolder = "/home/" + os.getlogin() + "/.steam/debian-installation/steamapps/common/American Truck Simulator/bin/linux_x64"
    else:
        fg("Failed to find American Truck Simulator folder. Please open steam and copy the game path and paste it below. or if the game is not installed leave blank and press enter")
        gamefolder = input()
        gamefolder = gamefolder.replace(" ", "")

    if gamefolder != "":

        if os.path.exists(gamefolder):
            if not os.path.exists(gamefolder + "/plugins"):
                folder = os.path.join(gamefolder, "plugins")
                os.system("mkdir -p \"" + folder + "\"")
            
            #Copy dlls
            try:
                os.system("cp -r ../helpers/dlls/Linux/* \"" + folder + "\"")
            except:
                print("Failed to copy dlls. Please copy them manually and try again.")

    

    

        
else:
    bg("\n┏ Installing DLLs...")
    bg("┗ This may take a while...\n")

    print("So......")
    print("I'm not going to install the dlls for you because I'm on linux but need something to put here so who ever is reading this could you do this for me or just wait a little?.")
# region CUDA

if CUDA:
    bg("\n┏ CUDA selected, installing...")
    bg("┗ This may take a while...\n")
    os.system(f"pip uninstall -y torch torchvision")
    os.system(f"pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
    bg("\n┏ CUDA done!")
    bg("┗ Continuing...\n")

fg("\n┏ [bold]Install done![/bold]")
if replace_input("┗ Do you want to start the app now? (Y/n) > ", default="y") == "n": sys.exit(0)
nl()
start_app()
