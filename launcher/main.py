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

start_command = 'start cmd /k "call helpers/environment.bat && cd app && python main.py"'

install_folder = "app"
is_installed = False

local_mode = False
dev_mode = False

try:
    git.Repo(install_folder)
    is_installed = True
except: pass

dpg.create_context()
with dpg.font_registry():
    regular_font = dpg.add_font('launcher/Geist-Regular.ttf', 18)

dpg.create_viewport(width=400, height=200, title=" ", clear_color=(20, 20, 20), small_icon="launcher/favicon.ico", large_icon="launcher/favicon.ico", resizable=False)
dpg.setup_dearpygui()

def get_readable_name(module: str):
    delimiters = ["-", "_", ".", " ", "=", ">", "<", "!", "?", ":", ";", "{", "}", "[", "]", "(", ")", "|", "&", "*", "^", "%", "$", "#", "@", "~", "`", "'", '"']
    index = 0
    for char in module:
        if char in delimiters:
            index = module.index(char)
            break
        
    return module[:index]

def get_index(lines: list[str], target: str):
    index = 0
    for line in lines:
        if target.lower() in line.lower() or target.lower() == line.lower():
            return index
        index += 1
    return -1

stop_updating = False
def update_thread(text = "Installing"):
    start_time = time.time()
    while not stop_updating:
        dpg.render_dearpygui_frame()
        dpg.set_viewport_title(f"{text} - {round(time.time() - start_time)}s")
        time.sleep(1)
        
    dpg.set_viewport_title(" ")

# https://github.com/ETS2LA/lite/blob/main/app/src/pytorch.py#L43
def pip_install_with_progress(requirements_file_path, progress_tag, step_progress, text_tag):
    dpg.configure_item(progress_tag, show=True)
    command = ["pip", "install", "-r", requirements_file_path, "--no-cache-dir", "--no-warn-script-location", "--disable-pip-version-check", "--progress-bar", "raw"]
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


def install_app():
    try:
        thread = threading.Thread(target=update_thread)
        thread.start()
        
        dpg.configure_item("button", show=False)
        dpg.configure_item("progress", overlay="Cloning...", default_value=-1, show=True)
        dpg.configure_item("installed_text", default_value="This step will download the latest version of ETS2LA.")

        git.Repo.clone_from("https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist.git", install_folder, multi_options=[
            " --depth=20",
            " --branch=rewrite",
            " --single-branch"
        ])

        dpg.configure_item("progress", overlay="Installing...")
        dpg.configure_item("installed_text", default_value="We are now downloading the required dependencies.\nThis will take a while depending on your internet.")

        pip_install_with_progress(f"{install_folder}/requirements.txt", "progress", "step_progress", "installed_text")

        global is_installed, stop_updating
        is_installed = True
        stop_updating = True

        update_ui()

    except Exception as e:
       print(f"Error during installation: {e}")

def remove_app():
    try:
        dpg.configure_item("button", enabled=False)
        dpg.configure_item("button", label="Removing...")
        dpg.configure_item("installed_text", default_value="Please restart the launcher.")

        os.system(f"rmdir /s /q {install_folder}")

        global is_installed
        is_installed = False

        update_ui()

    except Exception as e:
       print(f"Error during removal: {e}")
       dpg.configure_item("button", enabled=True)

def start_app():
    try:
        os.system(start_command)
        print("App started in a separate process.")
        exit()

    except Exception as e:
        print(f"Error starting the app: {e}")

def update_ui():
    """Updates the UI based on the installation state."""
    dpg.configure_item("installed_text", show=not is_installed)
    dpg.configure_item("dev_mode_checkbox", show=is_installed)
    dpg.configure_item("local_mode_checkbox", show=is_installed)
    dpg.configure_item("button", label="Start ETS2LA" if is_installed else "Install ETS2LA", callback=start_app if is_installed else install_app, show=True)
    dpg.configure_item("remove_button", show=is_installed)


with dpg.window(tag="Window", no_title_bar=True, no_resize=True, no_move=True, no_collapse=True, no_close=True, no_background=True) as window:
    with dpg.group(horizontal=True, horizontal_spacing=20, indent=10):
        dpg.add_checkbox(label="Dev Mode", tag="dev_mode_checkbox", callback=lambda s, a: print(f"Dev mode: {a}"), default_value=dev_mode)
        dpg.add_checkbox(label="Local Mode", tag="local_mode_checkbox", callback=lambda s, a: print(f"Local mode: {a}"), default_value=local_mode)
    
    with dpg.group(indent=10):
        dpg.add_spacer(height=10)
        dpg.add_text(default_value="ETS2LA is not installed.", tag="installed_text")
        dpg.add_button(label="Install ETS2LA", tag="button", callback=install_app, width=384 - 18 * 2)
        dpg.add_button(label="Remove ETS2LA", tag="remove_button", callback=remove_app, width=384 - 18 * 2, show=False)
        dpg.add_spacer(height=10)
        dpg.add_progress_bar(default_value=-1, overlay="Progress", tag="progress", show=False, width=384 - 18 * 2, height=26)
        dpg.add_progress_bar(default_value=-1, overlay="Progress", tag="step_progress", show=False, width=384 - 18 * 2, height=26)
        
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

dpg.start_dearpygui()
dpg.destroy_context()
exit()