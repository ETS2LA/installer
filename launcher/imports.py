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