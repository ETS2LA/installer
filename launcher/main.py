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
#endregion

start_command = "call helpers/environment.bat && cd app && python main.py"
console_command = "call helpers/environment.bat && cd app"

install_folder = "app"
is_installed = False

sure_to_install = False
sure_to_uninstall = False

github_link = "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist.git"
gitlab_link = "https://gitlab.com/ETS2LA/ETS2LA"
sourceforge_link = "https://git.code.sf.net/p/eurotrucksimulator2-laneassist/code"

download_server = "Download from GitHub"

state = " "
state_start_time = 0

try:
    git.Repo(install_folder)
    is_installed = True
except: pass

dpg.create_context()
with dpg.font_registry():
    regular_font = dpg.add_font('launcher/Geist-Regular.ttf', 18)

dpg.create_viewport(width=400, height=200, title=" ", clear_color=(20, 20, 20), 
                    small_icon="launcher/favicon.ico", large_icon="launcher/favicon.ico", 
                    resizable=False)
dpg.setup_dearpygui()

# Convert a package name to a readable name that (hopefully) matches the package name.
def get_readable_name(module: str):
    delimiters = ["-", "_", ".", " ", "=", ">", "<", "!", "?", ":", ";", "{", "}", 
                  "[", "]", "(", ")", "|", "&", "*", "^", "%", "$", "#", "@", "~", 
                  "`", "'", '"']
    index = 0
    for char in module:
        if char in delimiters:
            index = module.index(char)
            break
        
    return module[:index]

# Match a package name to a line in the requirements file to get the progress.
def get_index(lines: list[str], target: str):
    index = 0
    for line in lines:
        if target.lower() in line.lower() or target.lower() == line.lower():
            return index
        index += 1
    return -1

# https://github.com/ETS2LA/lite/blob/main/app/src/pytorch.py#L43
def pip_install_with_progress(requirements_file_path, progress_tag, step_progress, text_tag):
    dpg.configure_item(progress_tag, show=True)
    command = ["pip", "install", "-r", requirements_file_path, "--no-cache-dir", 
               "--no-warn-script-location", "--disable-pip-version-check", 
               "--progress-bar", "raw"]
    try:
        lines = open(requirements_file_path, "r").readlines()
        count = len(lines)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        current_module = ""
        line = 0

        while psutil.pid_exists(process.pid):
            time.sleep(0.05)
            output = process.stdout.readline()
            sys.stdout.write(output)
            
            if "Progress" in output:
                dpg.configure_item(step_progress, show=True)
                output = str(output.strip()).replace("Progress ", "").split(" of ")
                if len(output) == 2:
                    TotalSize = output[1]
                    DownloadedSize = output[0]
                    try:
                        percentage = round((int(DownloadedSize) / int(TotalSize)) * 100)
                        dpg.configure_item(step_progress, overlay=f"Downloading {percentage}%", default_value=percentage / 100)
                    except ValueError:
                        dpg.configure_item(step_progress, overlay=f"Downloading", default_value=0)
            
            elif "Downloading" in output and "metadata" not in output:
                current_module = output.split("Downloading ")[1].strip()
                dpg.configure_item(progress_tag, overlay=f"{line}/{count} - Collecting {get_readable_name(current_module)}", default_value=int(line)/int(count))
                        
            elif "Installing build dependencies: started" in output:
                dpg.configure_item(step_progress, show=False)
                dpg.configure_item(progress_tag, overlay=f"{line}/{count} - Installing {get_readable_name(current_module)} build dependencies", default_value=int(line)/int(count))
                        
            elif "Collecting" in output:
                dpg.configure_item(step_progress, show=False)
                current_module = output.split("Collecting ")[1].split(" ")[0].strip()
                dpg.configure_item(progress_tag, overlay=f"{line}/{count} - Collecting {get_readable_name(current_module)}", default_value=int(line)/int(count))
                
            elif "already satisfied" in output:
                dpg.configure_item(step_progress, show=False)
                current_module = output.split("Requirement already satisfied: ")[1].split(" in ")[0].strip()
                dpg.configure_item(progress_tag, overlay=f"{line}/{count} - Already satisfied {get_readable_name(current_module)}", default_value=int(line)/int(count))

            elif "Installing collected packages" in output:
                dpg.configure_item(step_progress, show=False)
                dpg.configure_item(text_tag, default_value="DO NOT CLOSE THIS WINDOW.\nThis step will take up to 30 minutes!")
                dpg.configure_item(progress_tag, overlay="Installing packages...", default_value=-1)

            index = get_index(lines, get_readable_name(current_module))
            if index != -1 and index != 1 and index != 0:
                if index > line:
                    line = index

        if process.returncode == 0 or process.returncode == None:
            dpg.configure_item(progress_tag, overlay="Install Finished!")
        else:
            dpg.configure_item(progress_tag, overlay="Install Failed!")
            print(f"Pip install failed with error code: {process.returncode}")
            print(f"Stderr: {process.stderr.read()}")

        dpg.configure_item(progress_tag, show=False)
        
    except Exception as e:
       dpg.configure_item(progress_tag, show=False)
       print(f"Error during installation: {e}")

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
              dpg.configure_item("progress", overlay=f"{self.last_message} {percent}%", default_value=percent / 100)

        # Reset percentage after each file:
        if op_code & (git.RemoteProgress.RECEIVING | git.RemoteProgress.COMPRESSING | git.RemoteProgress.RESOLVING):
            if cur_count == max_count and max_count > 0: # Check if the step is about to end
                self.last_percent = 0

def install_app():
    global sure_to_install, state, state_start_time
    if not sure_to_install:
        dpg.configure_item("button", label="Are you sure?", callback=install_app)
        sure_to_install = True
        return
    
    sure_to_install = False
    try:
        state = "Installing"
        state_start_time = time.time()
        dpg.configure_item("progress_spacer", height=10)
        
        dpg.configure_item("button", show=False)
        dpg.configure_item("download_server", show=False)
        dpg.configure_item("progress", overlay="Cloning...", default_value=-1, show=True)
        dpg.configure_item("installed_text", default_value="We are now downloading the ETS2LA codebase. This will take a while depending on your internet.")

        link = ""
        download_server = dpg.get_value("download_server")
        if download_server == "Download from GitHub":
            link = github_link
        elif download_server == "Download from GitLab":
            link = gitlab_link
        elif download_server == "Download from SourceForge":
            link = sourceforge_link

        git.Repo.clone_from(link, install_folder, multi_options=[
            " --depth=20",
            " --branch=rewrite",
            " --single-branch"
        ], progress=CloneProgress())
        
        # Check that the repo actually got cloned
        if os.path.exists(install_folder):
            if os.path.exists(f"{install_folder}/requirements.txt"):
                dpg.configure_item("progress", overlay="Installing...")
                dpg.configure_item("installed_text", default_value="We are now downloading the required dependencies. This will take a while depending on your internet.")

                pip_install_with_progress(f"{install_folder}/requirements.txt", "progress", "step_progress", "installed_text")

                global is_installed, stop_updating
                is_installed = True
                stop_updating = True

                state = " "
                    
                dpg.configure_item("progress_spacer", height=0)
                update_ui()
                return
            
        state = " "
        dpg.configure_item("progress_spacer", height=0)
        print("Error: The repository was not cloned successfully. Please try a different download server.")
        update_ui()

    except Exception as e:
        dpg.configure_item("progress_spacer", height=0)
        state = " "
        print(f"Error during installation: {e}")

def remove_app():
    global sure_to_uninstall
    if not sure_to_uninstall:
        dpg.configure_item("remove_button", label="Are you sure?", callback=remove_app)
        sure_to_uninstall = True
        return
    
    sure_to_uninstall = False
    try:
        dpg.configure_item("button", show=False)
        dpg.configure_item("installed_text", show=False)
        dpg.configure_item("console_button", show=False)
        dpg.configure_item("download_server", show=False)
        dpg.configure_item("dev_mode_checkbox", show=False)
        dpg.configure_item("local_mode_checkbox", show=False)
        dpg.configure_item("hide_console_checkbox", show=False)
        dpg.configure_item("no_ui_checkbox", show=False)

        dpg.configure_item("remove_button", label="Uninstalling requirements...")
        os.system(f"pip uninstall -r {install_folder}/requirements.txt -y")
        dpg.configure_item("remove_button", label="Removing ETS2LA...")
        os.system(f"rmdir /s /q {install_folder}")
        dpg.configure_item("remove_button", label="Restoring launcher requirements...", show=True)
        os.system("pip install wheel setuptools poetry dearpygui psutil")

        global is_installed
        is_installed = False

        dpg.configure_item("installed_text", default_value="Please restart the launcher.", show=True)
        update_ui()

    except Exception as e:
       print(f"Error during removal: {e}")
       dpg.configure_item("button", enabled=True)

def start_app():
    try:
        command = start_command
        if dpg.get_value("dev_mode_checkbox"):
            command += " --dev"
        if dpg.get_value("local_mode_checkbox"):
            command += " --local"
            
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

def update_ui():
    """Updates the UI based on the installation state."""
    dpg.configure_item("installed_text", show=not is_installed)
    dpg.configure_item("dev_mode_checkbox", show=is_installed)
    dpg.configure_item("local_mode_checkbox", show=is_installed)
    dpg.configure_item("hide_console_checkbox", show=is_installed)
    dpg.configure_item("no_ui_checkbox", show=is_installed)
    dpg.configure_item("button", label="Start ETS2LA" if is_installed else "Install ETS2LA", callback=start_app if is_installed else install_app, show=True)
    dpg.configure_item("remove_button", show=is_installed)
    dpg.configure_item("console_button", show=is_installed)
    dpg.configure_item("download_server", show=not is_installed)


with dpg.window(tag="Window", no_title_bar=True, no_resize=True, no_move=True, no_collapse=True, no_close=True, no_background=True, no_scrollbar=True) as window:
    with dpg.group(horizontal=True, horizontal_spacing=20, indent=10):
        dpg.add_checkbox(label="Dev Mode", tag="dev_mode_checkbox", default_value=False)
        with dpg.tooltip("dev_mode_checkbox", hide_on_activity=True, delay=0.1):
            dpg.add_text("Enable development mode. Will refresh plugins on code changes and display plugins marked as WIP.", wrap=200)
            
        dpg.add_spacer(width=27)
        dpg.add_checkbox(label="Local Mode", tag="local_mode_checkbox", default_value=False)
        with dpg.tooltip("local_mode_checkbox", hide_on_activity=True, delay=0.1):
            dpg.add_text("Will attempt to run the user interface locally. Requires NodeJS!", wrap=200)
        
    with dpg.group(horizontal=True, horizontal_spacing=20, indent=10):
        dpg.add_checkbox(label="Hide Console", tag="hide_console_checkbox", default_value=False)
        with dpg.tooltip("hide_console_checkbox", hide_on_activity=True, delay=0.1):
            dpg.add_text("This will hide the console after the UI has been loaded.", wrap=200)
            
        dpg.add_spacer(width=6)
        
        dpg.add_checkbox(label="Use Browser", tag="no_ui_checkbox", default_value=False)
        with dpg.tooltip("no_ui_checkbox", hide_on_activity=True, delay=0.1):
            dpg.add_text("This will disable the inbuilt UI and open the app in a browser.", wrap=200)
    
    with dpg.group(indent=10):
        dpg.add_text(default_value=f"ETS2LA will be installed to:\n{os.path.abspath(install_folder)}", tag="installed_text", show=not is_installed, wrap=384 - 18 * 2)
        dpg.add_spacer(height=0, tag="progress_spacer")
        dpg.add_progress_bar(default_value=-1, overlay="Progress", tag="progress", show=False, width=384 - 18 * 2, height=26)
        dpg.add_progress_bar(default_value=-1, overlay="Progress", tag="step_progress", show=False, width=384 - 18 * 2, height=26)
        dpg.add_spacer(height=10)
        dpg.add_button(label="Install ETS2LA", tag="button", callback=install_app, width=384 - 18 * 2)
        dpg.add_combo(label="", items=["Download from GitHub", "Download from GitLab", "Download from SourceForge"], tag="download_server", default_value=download_server, width=384 - 18 * 2)
        with dpg.tooltip("download_server", hide_on_activity=True, delay=0.1):
            dpg.add_text("People in places where GitHub is blocked should use GitLab or SourceForge instead.", wrap=200)
        
        dpg.add_button(label="Open Console", tag="console_button", callback=open_console, width=384 - 18 * 2, show=False)
        dpg.add_spacer(height=30)
        dpg.add_button(label="Remove ETS2LA", tag="remove_button", callback=remove_app, width=384 - 18 * 2, show=False)
        
    update_ui()  # Initial UI setup based on is_installed


with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (32, 32, 32), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border, (32, 32, 32), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (37, 37, 38), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)


dpg.bind_font(regular_font)
dpg.bind_theme(global_theme)
dpg.set_primary_window("Window", True)
dpg.show_viewport()

if pywinstyles and os.name == "nt":
    print("Applying dark theme...")
    pywinstyles.apply_style(None, "dark")

while dpg.is_dearpygui_running():
    if state_start_time != 0 and state != " ":
        dpg.set_viewport_title(f"{state} - {round(time.time() - state_start_time)}s")
    elif state_start_time != 0 and state == " ":
        dpg.set_viewport_title(" ")
        state_start_time = 0
        
    dpg.render_dearpygui_frame()

dpg.destroy_context()
exit()