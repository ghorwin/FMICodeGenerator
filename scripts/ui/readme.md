# Qt-Ui files for the graphical user interface

UI-files are converted to Python scripts (PyQt6):

```bash
> pyuic6 -i 0 file.ui -o ../Ui_file.py
```

PyQt6 no longer ships a resource compiler (`pyrcc`), so there is no `.qrc` resource file.
The icons for the tool buttons are stored in `gfx/` and are loaded at runtime from that
directory (see `WizardPageVariables.py`). When adding icons, put them into `gfx/` and set them
in the Python code, not via a resource in Qt Designer.

To automate the process (which needs to be done whenever a ui file has been edited) the
script `update.sh` is available. Run this, whenever you have modified a ui file!
