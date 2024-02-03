This installer is actually just used to download the actual installer.

It's just easier to have a python installer first to check for any problems in the install location etc...


Originally I was going to use Inno Setup, but unfortunately that triggeres the windows antivirus checks (AND NO ONE ELSE) so that means that we are now using a python file converted to .exe


### Build instructions

1. Download auto-py-to-exe
2. Select the file, set to one file mode.
3. Advanced - Collect all - Set one to sv_ttk
4. Build

### Usage

Prebuilt versions can be found in output/installer.exe