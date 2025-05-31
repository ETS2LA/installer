## ETS2LA Installer
This repository contains the installer for ETS2LA. You can find the source code for the main application in the [ETS2LA repository](https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist).

### Downloads
- Check the [releases](https://github.com/ETS2LA/installer/releases/latest) page for the latest automatically built installer.
- You can check out [ets2la.com/developers](https://ets2la.com/developers) for the latest information on setting up a development environment for **ETS2LA**.

### Building the Installer
Install NSIS from [nsis.sourceforge.io](https://nsis.sourceforge.io/Download) and Python from [python.org](https://www.python.org/downloads/). Then run the following commands in the root directory of this repository:

```bash
python auto_precompile.py
makensis main.nsi
```

### Contributing Translations
Please refer to the [translation guide](TRANSLATION.md) for information on how to contribute translations for the installer.

### Contributing Code
Please fork the repository and create a PR with your changes.