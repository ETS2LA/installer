from rich.console import Console
import psutil
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
    if input("Continue? (Y/n) ") == "n": sys.exit(1)
def nl():
    console.print()
def replace_input(text, default=None):
    default = text + default if default else ""
    response = console.input(text)
    if response == "": 
        sys.stdout.write("\033[F") # Move cursor up
        sys.stdout.write("\033[K")
        console.print(default)
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

DIR =  sys.path[0]
VER = sys.version.split(" ")[0]
NODE_VER = os.popen("node -v").read().strip()
RAM = psutil.virtual_memory().total / 1024 / 1024 / 1024
CORES = psutil.cpu_count()
GITHUB_URL = "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist.git"
SOURCEFORGE_URL = "ssh://tumppi066@git.code.sf.net/p/eurotrucksimulator2-laneassist/code"
CLONED = os.path.exists(DIR + "\\app")


bg("┏ Hi, I'm the installer!")

bg("┣ I'm running in [bold]" + DIR + "[/bold]")
bg("┣ Python version: [cyan][bold]" + VER + "[/cyan][/bold]")
bg("┣ Node version: [cyan][bold]" + NODE_VER + "[/cyan][/bold]")

bg("┣ RAM: " + str(round(RAM, 1)) + " GB", end=" > ")
if RAM < 8: err("You have less than 8 GB of RAM. This may cause problems.")
elif RAM < 12: warn("You have less than 12 GB of RAM. It should be fine if you don't use chrome.")
else: bg("[bold]OK[/bold]")

bg("┗ Cores: " + str(CORES), end=" > ")
if CORES < 4: err("You have less than 4 CPU cores. This may cause problems as the app is very much multi-threaded.")
elif CORES < 6: warn("You have less than 6 CPU cores. You should be fine... I think.")
else: bg("[bold]OK[/bold]")

nl()

bg("┏ Checking if the app is already cloned...")
bg("┗ " + ("It is - starting the app." if CLONED else "It's not - starting the install now."))

nl()

if CLONED:
    start_app()
    sys.exit(0)

fg("┏ Let's ask some questions to get you started.")
IS_IN_LIMITED_COUNTRY = replace_input("┣ Are you in a [i]country[/i] where you can't access [blue][bold]GitHub[/bold][/blue]? (y/N) > ", default="n") == "n"
HAS_NVIDIA = replace_input("┣ Do you have an [bold][green]NVIDIA[/green][/bold] GPU? (y/N) > ", default="n") == "y"
CUDA = False
if HAS_NVIDIA: CUDA = replace_input("┣ NVIDIA version for better performance? It requires 2gb more space. (Y/n) > ", default="y") != "n"
if replace_input("┣ ETS2LA will be installed to [bold]" + DIR + "\\app[/bold]. Continue? (Y/n) > ", default="y") == "n": sys.exit(1)
wait("┗ ", 2)

bg("\n┏ Starting install...")
bg(f"┗ Cloning from {'[yellow][bold]sourceforge[/bold][/yellow]' if IS_IN_LIMITED_COUNTRY else '[blue][bold]GitHub[/bold][/blue]'}...\n")

if IS_IN_LIMITED_COUNTRY:
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

fg("\n┏ [bold]Install done![/bold]")
if replace_input("┗ Do you want to start the app now? (Y/n) > ", default="y") == "n": sys.exit(0)
nl()
start_app()