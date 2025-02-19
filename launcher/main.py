#region Imports
import subprocess
import threading
import time
import sys
import os

try:
    import psutil
except:
    os.system("pip install psutil")
    import psutil

try:
    import dearpygui.dearpygui as dpg
except:
    os.system("pip install dearpygui")
    import dearpygui.dearpygui as dpg

try:
    import pywinstyles
except:
    try:
        os.system("pip install pywinstyles")
        import pywinstyles
    except:
        pywinstyles = None

try:
    import git
except:
    os.system("pip install GitPython")
    import git

try:
    import DearPyGui_Markdown as dpg_md
except:
    os.system("pip install -e additional_modules/DearPyGui-Markdown-main")
    print("\n-> PLEASE RESTART THE LAUNCHER TO APPLY THE CHANGES!")
    input("Press any key to exit...")
    exit()

#endregion

markdown_root = "launcher/pages"

start_command = "call helpers/environment.bat && cd app && python main.py"
console_command = "call helpers/environment.bat && cd app"

install_folder = "app"
is_installed = False

sure_to_install = False
sure_to_uninstall = False

github_link = "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist.git"
gitlab_link = "https://gitlab.com/ETS2LA/ETS2LA"
sourceforge_link = "https://git.code.sf.net/p/eurotrucksimulator2-laneassist/code"

download_server = "GitHub"

pages = [] # This will be populated at the end.

try:
    git.Repo(install_folder)
    is_installed = True
except: pass

dpg.create_context()

dpg_md.set_font_registry(dpg.add_font_registry())
dpg_font = dpg_md.set_font(
    font_size=18,
    default="launcher/Geist-Regular.ttf",
    bold="launcher/Geist-Bold.ttf",
    italic="launcher/Geist-Regular.ttf",
    italic_bold="launcher/Geist-Bold.ttf"
)
dpg.bind_font(dpg_font)

dpg.create_viewport(width=500, height=350, title=" ", 
                    small_icon="launcher/favicon.ico", large_icon="launcher/favicon.ico", 
                    resizable=False)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.render_dearpygui_frame() # render first frame to avoid deadlock on wrapping.
dpg.render_dearpygui_frame()

# Convert a package name to a readable name that (hopefully) matches the package name.
def get_readable_name(module: str):
    delimiters = [".", " ", "=", ">", "<", "!", "?", ":", ";", "{", "}", 
                  "[", "]", "(", ")", "|", "&", "*", "^", "%", "$", "#", "@", "~", 
                  "`", "'", '"']
    index = 0
    for char in module:
        if char in delimiters or char.isdigit():
            index = module.index(char)
            break
        
    if index == 0:
        return module
        
    name = module[:index]
    if name[-1] == "-" or name[-1] == "_":
        name = name[:-1]
        
    return name

# Match a package name to a line in the requirements file to get the progress.
def get_index(lines: list[str], target: str):
    index = 0
    for line in lines:
        test_target = target.replace("-", "_")
        if test_target.lower() in line.lower() or test_target.lower() == line.lower():
            return index
        
        test_target = target.replace("_", "-")
        if test_target.lower() in line.lower() or test_target.lower() == line.lower():
            return index
        index += 1
    return -1

# https://github.com/ETS2LA/lite/blob/main/app/src/pytorch.py#L43
def pip_install_with_progress(requirements_file_path):
    command = ["pip", "install", "-r", requirements_file_path, "--no-cache-dir", 
               "--no-warn-script-location", "--disable-pip-version-check", 
               "--progress-bar", "raw"]
    
    index_urls = []
    
    if dpg.get_value("nvidia"):
        index_urls += ["https://download.pytorch.org/whl/cu126"]
    if dpg.get_value("tsinghua"):
        index_urls += ["https://pypi.tuna.tsinghua.edu.cn/simple"]
    else:
        index_urls += ["https://pypi.org/simple"] # Default index.
        
    if len(index_urls) == 2:
        # Pytorch index first to download the cuda version if available.
        command += ["--index-url", index_urls[0], "--extra-index-url", index_urls[1]]
    elif len(index_urls) == 1:
        command += ["--index-url", index_urls[0]]
        
    try:
        lines = open(requirements_file_path, "r").readlines()
        count = len(lines)
        completed_lines = []
        
        current_module = ""
        
        last_progress_time = time.time()
        last_downloaded_size = 0
        download_speeds = []
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        dpg.configure_item("requirements_progress_text", default_value="Gathering metadata...")
        while psutil.pid_exists(process.pid):
            output = process.stdout.readline()
            sys.stdout.write(output)
            
            if "Progress" in output:
                output = str(output.strip()).replace("Progress ", "").split(" of ")
                if len(output) == 2:
                    downloaded_size = int(output[0])
                    total_size = int(output[1])
                    
                    if downloaded_size != last_downloaded_size:
                        download_speeds.append((int(downloaded_size) - last_downloaded_size) / (time.time() - last_progress_time))
                        if len(download_speeds) > 30:
                            download_speeds.pop(0)
                        
                        last_downloaded_size = int(downloaded_size)
                        last_progress_time = time.time()
                    
                    try:
                        percentage = round((downloaded_size / total_size) * 100)
                        text = f"{len(completed_lines)}/{count} - Collecting {get_readable_name(current_module)} {percentage}%"
                        if total_size > 5_000_000: # 5mb
                            if len(download_speeds) == 0 or sum(download_speeds) == 0:
                                text += "\nCalculating remaining time -"
                            else:
                                left = (total_size - downloaded_size) / (sum(download_speeds) / len(download_speeds))
                                minutes = int(left / 60)
                                seconds = int(left % 60)
                                if seconds >= 0 and minutes >= 0:
                                    text += f"\n{minutes}m {seconds}s remaining -"
                                else:
                                    text += "\nCalculating remaining time -"
                                    
                            text += f" {int(downloaded_size / 1_000_000)}mb/{int(total_size / 1_000_000)}mb"
                            text += f" @ {(sum(download_speeds) / len(download_speeds)) / 1_000_000:.2f}mb/s"
                            
                        dpg.configure_item("requirements_progress_text", default_value=text)
                    except ValueError:
                        ...
            
            elif "Downloading" in output and "metadata" not in output and "https://" not in output:
                module = output.split("Downloading ")[1].strip()
                if module != "":
                    last_downloaded_size = 0
                    download_speeds = [0]
                    current_module = module 
                dpg.configure_item("requirements_progress", default_value=int(len(completed_lines))/int(count), overlay=f"{len(completed_lines)/count * 100:.0f}%")
                dpg.configure_item("requirements_progress_text", default_value=f"{len(completed_lines)}/{count} - Collecting {get_readable_name(current_module)}")
                
            elif "Downloading" in output and "metadata" not in output and "download.pytorch.org" in output:
                # Hard code to downloading torch
                current_module = "torch"
                download_speeds = [0]
                last_downloaded_size = 0
                dpg.configure_item("requirements_progress", default_value=int(len(completed_lines))/int(count), overlay=f"{len(completed_lines)/count * 100:.0f}%")
                dpg.configure_item("requirements_progress_text", default_value=f"{len(completed_lines)}/{count} - Collecting {get_readable_name(current_module)}")
            
            elif "Downloading" in output and "metadata" in output:
                module = output.split("Downloading ")[1].strip()
                dpg.configure_item("requirements_progress_text", default_value=f"Gathering {get_readable_name(module)} metadata")   
            
            elif "Building wheel for " in output:
                module = output.split("Building wheel for ")[1].split(" (setup.py)")[0].strip()
                if module != "":
                    current_module = module
                dpg.configure_item("requirements_progress", default_value=int(len(completed_lines))/int(count), overlay=f"{len(completed_lines)/count * 100:.0f}%")
                dpg.configure_item("requirements_progress_text", default_value=f"{len(completed_lines)}/{count} - Building wheel for {get_readable_name(current_module)}")
                        
            elif "Installing build dependencies: started" in output:
                dpg.configure_item("requirements_progress", default_value=int(len(completed_lines))/int(count), overlay=f"{len(completed_lines)/count * 100:.0f}%")
                dpg.configure_item("requirements_progress_text", default_value=f"{len(completed_lines)}/{count} - Installing {get_readable_name(current_module)} build dependencies")
                        
            elif "already satisfied" in output:
                current_module = output.split("Requirement already satisfied: ")[1].split(" in ")[0].strip()
                dpg.configure_item("requirements_progress", default_value=int(len(completed_lines))/int(count), overlay=f"{len(completed_lines)/count * 100:.0f}%")
                dpg.configure_item("requirements_progress_text", default_value=f"{len(completed_lines)}/{count} - Already satisfied {get_readable_name(current_module)}")
                
            elif "Installing collected packages" in output:
                dpg.configure_item("requirements_progress", default_value=int(len(completed_lines))/int(count), overlay=f"{(count-1)/count * 100:.0f}%")
                dpg.configure_item("requirements_progress_text", default_value=f"Installing collected Python packages.\nThis can take up to 30 minutes.")

            index = get_index(lines, get_readable_name(current_module))
            if index != -1:
                if index not in completed_lines:
                    completed_lines.append(index)

        if process.returncode == 0 or process.returncode == None:
            ...
        else:
            #dpg.configure_item(progress_tag, overlay="Install Failed!")
            print(f"Pip install failed with error code: {process.returncode}")
            print(f"Stderr: {process.stderr.read()}")
        
    except Exception as e:
       print(f"Error during installation: {e}")
       import traceback
       traceback.print_exc()

# Git progress handler.
class CloneProgress(git.RemoteProgress):
    def __init__(self):
        super().__init__()
        self.total_ops = 0
        self.completed_ops = 0
        self.last_percent = 0
        self.last_message = "Cloning..."
        
    def update(self, op_code, cur_count, max_count=None, message=""):
        if message != self.last_message and message != "":
            self.last_message = message
        
        if max_count is not None:
            percent = round((cur_count / max_count) * 100)

            if percent != self.last_percent:
                dpg.configure_item("cloning_progress", default_value=percent / 100, overlay=f"{percent}%")
                dpg.configure_item("cloning_progress_text", default_value=f"{self.last_message}")

        # Reset percentage after each file:
        if op_code & (git.RemoteProgress.RECEIVING | git.RemoteProgress.COMPRESSING | git.RemoteProgress.RESOLVING):
            if cur_count == max_count and max_count > 0: # Check if the step is about to end
                self.last_percent = 0


def install_app():
    try:
        #dpg.configure_item("installed_text", default_value="We are now downloading the ETS2LA codebase. This will take a while depending on your internet.")
        
        # Check that the repo actually got cloned
        if os.path.exists(install_folder):
            if os.path.exists(f"{install_folder}/requirements.txt"):
                #dpg.configure_item("progress", overlay="Installing...")
                #dpg.configure_item("installed_text", default_value="We are now downloading the required dependencies. This will take a while depending on your internet.")

                pip_install_with_progress(f"{install_folder}/requirements.txt", "progress", "step_progress", "installed_text")

                global is_installed, stop_updating
                is_installed = True
                stop_updating = True

                    
                return
            
        print("Error: The repository was not cloned successfully. Please try a different download server.")

    except Exception as e:
        print(f"Error during installation: {e}")


def remove_app():
    try:
        #dpg.configure_item("remove_button", label="Uninstalling requirements...")
        os.system(f"pip uninstall -r {install_folder}/requirements.txt -y")
        os.system(f"pip cache purge")
        #dpg.configure_item("remove_button", label="Removing ETS2LA...")
        os.system(f"rmdir /s /q {install_folder}")
        #dpg.configure_item("remove_button", label="Restoring launcher requirements...", show=True)
        os.system("pip install wheel setuptools poetry dearpygui psutil")

        global is_installed
        is_installed = False

        #dpg.configure_item("installed_text", default_value="Please restart the launcher.", show=True)

    except Exception as e:
       print(f"Error during removal: {e}")
       dpg.configure_item("button", enabled=True)


def start_app():
    try:
        command = start_command
        #if dpg.get_value("dev_mode_checkbox"):
        #    command += " --dev"
        #if dpg.get_value("local_mode_checkbox"):
        #    command += " --local"
            
        print(f"Starting app with command: {command}")
        os.system(f'start cmd /k "{command}"')
        print("App started in a separate process.")

    except Exception as e:
        print(f"Error starting the app: {e}")
   
        
def open_console():
    try:
        os.system(f'start cmd /k "{console_command}"')
        print("Console opened in a separate process.")
    except Exception as e:
        print(f"Error opening the console: {e}")


def on_resize(_ , position):
    width = position[0]
    height = position[1]
    
    # Anchor buttons
    dpg.set_item_pos("next", [width - 114, height - 80])
    dpg.set_item_pos("back", [18, height - 80])
    
    
def turn_page(index: int):
    pages_list = list(pages.keys())
    exiting_last_page = pages_list[index - 2] if index - 2 >= 0 else None
    exiting_page = pages_list[index - 1] if index - 1 >= 0 else None
    entering_page = pages_list[index]
    next_page = pages_list[index + 1] if index + 1 < len(pages_list) else None
        
    next_text = pages[entering_page].get("next", "Next")
    back_text = pages[entering_page].get("back", "Back")
    print(f"Turning page: {entering_page}")
    print(f"Back_text: {back_text}")
        
    dpg.configure_item(entering_page, show=True)
    
    if exiting_page:
        dpg.configure_item(exiting_page, show=False)
        if back_text != "":
            dpg.configure_item("back", label=back_text, callback=lambda: turn_page(index - 1), show=True)
        else:
            dpg.configure_item("back", show=False)
    else:
        dpg.configure_item("back", show=False)
        
    if next_page:
        dpg.configure_item(next_page, show=False)
        if next_text != "":
            dpg.configure_item("next", label=next_text, callback=lambda: turn_page(index + 1), show=True)
        else:
            dpg.configure_item("next", show=False)
    else:
        dpg.configure_item("next", show=False)
        
    if pages[entering_page].get("update"):
        pages[entering_page]["update"]()
        
        
def hide_navigation():
    dpg.configure_item("back", show=False)
    dpg.configure_item("next", show=False)
    
def show_navigation():
    dpg.configure_item("back", show=True)
    dpg.configure_item("next", show=True)
    

with dpg.window(tag="Navigation", no_title_bar=True, no_resize=True, no_move=True, no_collapse=True, no_close=True, no_background=False, no_scrollbar=True, show=True, width=500, height=350) as window:
    dpg.add_button(label="Back", tag="back", callback=lambda: turn_page(0), width=80)
    dpg.add_button(label="Next", tag="next", callback=lambda: turn_page(1), width=80)
    
    
with dpg.window(tag="Welcome", no_title_bar=True, no_collapse=True, no_close=True, no_resize=True, no_move=True, no_background=True, no_scrollbar=True, show=False, width=500, height=270) as window:
    install_text = open(f"{markdown_root}/welcome.md", "r", encoding="utf-8").read()
    with dpg.group(indent=10):
        dpg_md.add_text(install_text, wrap=484 - 18 * 2)


with dpg.window(tag="SystemCheck", no_title_bar=True, no_collapse=True, no_close=True, no_resize=True, no_move=True, no_background=True, no_scrollbar=True, show=False, width=500, height=270) as window:
    ram = round(psutil.virtual_memory().total / 1024 / 1024 / 1024)
    cores = psutil.cpu_count()
    space = psutil.disk_usage(os.path.abspath(os.sep)).free / 1024 / 1024 / 1024

    system_check_text = open(f"{markdown_root}/system_check.md", "r", encoding="utf-8").read()
    with dpg.group(indent=10):
        dpg_md.add_text(system_check_text, wrap=484 - 18 * 2)
        dpg.add_spacer(height=5)
        
    with dpg.group(indent=3):
        if ram < 12:
            dpg_md.add_text("> **ERROR**:\nETS2LA requires 10GB of RAM or more.", wrap=484 - 18 * 2)
        elif ram < 16:
            dpg_md.add_text("> **WARNING**:\nETS2LA recommends 16GB of RAM or more.", wrap=484 - 18 * 2)
        else:
            dpg_md.add_text(f"> RAM: {ram:.0f} GB -> **OK**", wrap=484 - 18 * 2)
        
        if cores < 4:
            dpg_md.add_text("> **ERROR**:\nETS2LA requires 4 cores or more.", wrap=484 - 18 * 2)
        elif cores < 8:
            dpg_md.add_text("> **WARNING**:\nETS2LA recommends 8 cores or more.", wrap=484 - 18 * 2)
        else:
            dpg_md.add_text(f"> CPU Cores: {cores} -> **OK**", wrap=484 - 18 * 2)
            
        if space < 6:
            dpg_md.add_text("> **ERROR**:\nETS2LA requires 6GB of free space.", wrap=484 - 18 * 2)
        elif space < 20:
            dpg_md.add_text("> **WARNING**:\nETS2LA recommends 20GB space.", wrap=484 - 18 * 2)
        else:
            dpg_md.add_text(f"> Free Storage: {space:.0f} GB -> **OK**", wrap=484 - 18 * 2)


with dpg.window(tag="InstallOptions", no_title_bar=True, no_collapse=True, no_close=True, no_resize=True, no_move=True, no_background=True, no_scrollbar=True, show=False, width=500, height=270) as window:
    install_options_text = open(f"{markdown_root}/install_options.md", "r", encoding="utf-8").read()
    with dpg.group(indent=10):
        dpg_md.add_text(install_options_text, wrap=484 - 18 * 2)
        dpg.add_spacer(height=5)
        
        with dpg.group(horizontal=True, horizontal_spacing=50):
            with dpg.group():
                dpg.add_text("Download server:")
                dpg.add_radio_button(["GitHub", "GitLab", "SourceForge"], tag="download_server", default_value="GitHub")
                
                with dpg.tooltip("download_server", hide_on_activity=True, delay=0.1):
                    dpg.add_text("Choose the server to download the codebase from. GitHub is recommended, if you don't have access to it then use GitLab.", wrap=200)
            
            with dpg.group():
                dpg.add_text("Additional options:")
                dpg.add_checkbox(label="Install with NVIDIA compatibility", tag="nvidia")
                dpg.add_checkbox(label="Use Tsinghua PyPI mirror", tag="tsinghua")
                
                with dpg.tooltip("nvidia", hide_on_activity=True, delay=0.1):
                    dpg.add_text("If you have an NVIDIA GPU, you can choose download the NVIDIA compatible version of packages for better performance.\n\nNOTE: Requires at least 3gb of extra storage!", wrap=200)
                with dpg.tooltip("tsinghua", hide_on_activity=True, delay=0.1):
                    dpg.add_text("Tsinghua is a Chinese university that hosts it's own PyPI mirror. If you have issues connecting to the official PyPI servers please enable this.", wrap=200)

def update_recap_page():
    dpg.configure_item("install_location", default_value=f"{os.path.abspath(install_folder)}")
    download_server_text = dpg.get_value("download_server") + " with Tsinghua PyPI mirror" if dpg.get_value("tsinghua") else dpg.get_value("download_server")
    dpg.configure_item("download_server_text", default_value=f"{download_server_text}")
    
with dpg.window(tag="Recap", no_title_bar=True, no_collapse=True, no_close=True, no_resize=True, no_move=True, no_background=True, no_scrollbar=True, show=False, width=500, height=270) as window:
    with dpg.group(indent=10):
        with dpg.group(horizontal=True, horizontal_spacing=50):
            with dpg.group():
                dpg_md.add_text_bold("Install location:")
                dpg.add_text(os.path.abspath(install_folder), wrap=484 - 18 * 2, tag="install_location")
                dpg.add_spacer(height=5)
                dpg_md.add_text_bold("Download server:")
                dpg.add_text("GitHub", tag="download_server_text")
                
                with dpg.tooltip("install_location", hide_on_activity=True, delay=0.1):
                    dpg.add_text("To change the install location please move the folder with start.bat", wrap=200)
    
def update_cloning_page():
    hide_navigation()
    dpg.render_dearpygui_frame() # Render the markdown
    
    if os.path.exists(install_folder):
        os.system(f"rmdir /s /q {install_folder}")
    
    link = ""
    download_server = dpg.get_value("download_server")
    if download_server == "GitHub":
        link = github_link
    elif download_server == "GitLab":
        link = gitlab_link
    elif download_server == "SourceForge":
        link = sourceforge_link

    git.Repo.clone_from(link, install_folder, multi_options=[
        " --depth=20",
        " --branch=rewrite",
        " --single-branch"
    ], progress=CloneProgress())
    
    start_time = time.time()
    wait_time = 3
    while True:
        time.sleep(0.1)
        time_till_start = round(time.time() - start_time)
        dpg.configure_item("cloning_progress_text", default_value=f"Done! Continuing in {wait_time - time_till_start} seconds...")
        if time_till_start >= wait_time:
            break
        
    turn_page(5)
    
with dpg.window(tag="Cloning", no_title_bar=True, no_collapse=True, no_close=True, no_resize=True, no_move=True, no_background=True, no_scrollbar=True, show=False, width=500, height=270) as window:
    cloning_text = open(f"{markdown_root}/cloning.md", "r", encoding="utf-8").read()
    with dpg.group(indent=10):
        dpg_md.add_text_bold(cloning_text.split("\n")[0].replace("*", ""))
        dpg.add_text(cloning_text.split("\n")[1], wrap=484 - 18 * 2)
        dpg.add_spacer(height=5)
        dpg.add_progress_bar(tag="cloning_progress", overlay="", default_value=0, width=484 - 18 * 2)
        dpg.add_text("Cloning...", tag="cloning_progress_text")
        
def update_requirements_page():
    hide_navigation()
    dpg.render_dearpygui_frame() # Render the markdown
    pip_install_with_progress(f"{install_folder}/requirements.txt")
    dpg.configure_item("requirements_progress_text", default_value="Done!")
    dpg.configure_item("requirements_progress", default_value=1, overlay="100%")
    dpg.configure_item("next", show=True)
        
with dpg.window(tag="Requirements", no_title_bar=True, no_collapse=True, no_close=True, no_resize=True, no_move=True, no_background=True, no_scrollbar=True, show=False, width=500, height=270) as window:
    requirements_text = open(f"{markdown_root}/requirements.md", "r", encoding="utf-8").read()
    with dpg.group(indent=10):
        dpg_md.add_text_bold(requirements_text.split("\n")[0].replace("*", ""))
        dpg.add_text(requirements_text.split("\n")[1], wrap=484 - 18 * 2)
        dpg.add_spacer(height=5)
        dpg.add_progress_bar(tag="requirements_progress", overlay="", default_value=0, width=484 - 18 * 2)
        dpg.add_text("Contacting Server...", tag="requirements_progress_text")
    
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (32, 32, 32), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border, (32, 32, 32), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (37, 37, 38), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)


pages = {
    "Welcome": {},
    "SystemCheck": {},
    "InstallOptions": {},
    "Recap": {
        "update": update_recap_page,
        "next": "Install",
    },
    "Cloning": {
        "update": update_cloning_page,
        "next": "Continue"
    },
    "Requirements": {
        "update": update_requirements_page,
        "back": "",
        "next": "Finish"
    }
}

dpg.bind_theme(global_theme)
dpg.set_viewport_resize_callback(on_resize)
on_resize(None, [500, 350])
dpg.set_primary_window("Navigation", True)

if not is_installed:
    dpg.configure_item("back", show=False)
    dpg.configure_item("Welcome", show=True)

if pywinstyles and os.name == "nt":
    print("Applying dark theme...")
    pywinstyles.change_header_color(None, "#202020")
    pywinstyles.change_title_color(None, "#909090")

while dpg.is_dearpygui_running():    
    dpg.render_dearpygui_frame()

dpg.destroy_context()
exit()