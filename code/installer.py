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
    try:
        start_app()
        sys.exit(0)
    except:
        err("┏ Something went wrong when starting.")
        fg("[red]┗ Removing the app and starting the install now.[/red]")
        try:
            shutil.rmtree(DIR + "\\app")
        except:
            err("\n┏ Couldn't remove the app folder. Please delete [code][bold]" + DIR + "\\app[/bold][/code] manually and restart the installer.")
            sys.exit(1)
    
# endregion

# region Install questions

fg("┏ Let's ask some questions to get you started.")
CAN_ACCESS_GITHUB = replace_input("┣ 1 - Can you access [blue][bold]GitHub[/bold][/blue] in your [i]country[/i]? (Y/n) > ", default="y") == "y"
HAS_NVIDIA = replace_input("┣ 2 - Do you have an [bold][green]NVIDIA[/green][/bold] GPU? (y/N) > ", default="n") == "y"
CUDA = False
if HAS_NVIDIA: CUDA = replace_input("┣ 3 - NVIDIA version for better performance? It requires 2gb more space. (Y/n) > ", default="y") == "y"
if replace_input("┣ [bold]OK[/bold] - ETS2LA will be installed to [bold]" + DIR + "\\app[/bold]. Continue? (Y/n) > ", default="y") == "n": sys.exit(1)
wait("┗ ", 2)

# endregion

# region Install

bg("\n┏ Starting install...")
bg(f"┗ Cloning from {'[yellow][bold]sourceforge[/bold][/yellow]' if not CAN_ACCESS_GITHUB else '[blue][bold]GitHub[/bold][/blue]'}...\n")

if not CAN_ACCESS_GITHUB:
    os.system(f"git clone {SOURCEFORGE_URL} {DIR}\\app")
else:
    os.system(f"git clone {GITHUB_URL} {DIR}\\app")
    
# Switch to the rewrite branch
os.system(f"cd {DIR}\\app && git checkout rewrite")
    
bg("\n┏ Git done, checking...")

if "requirements.txt" not in os.listdir(DIR + "\\app"):
    err("┗ Something went wrong. The app wasn't cloned properly.")
    input("Press enter to exit.")

bg("┣ Cloned successfully, continuing...")
bg("┗ Installing python dependencies...\n")

os.system(f"pip install -r {DIR}\\app\\requirements.txt")

bg("\n┏ Dependencies done, continuing...")
bg("┗ Setting up node...\n")

os.system(f"cd {DIR}\\app\\frontend && npm install")

# endregion

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