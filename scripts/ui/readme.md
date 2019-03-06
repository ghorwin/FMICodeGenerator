# Qt-Ui files for the graphical user interface

UI-files are converted to Python scripts:

```bash
> pyuic5 file.ui > -o file.py
```

The ui files use a resource file FMIGenerator.qrc that holds images for icons/tool buttons.
When converting ui-files to python scripts, the resource file is imported by name
`FMIGenerator_rc.py`. We use the qrc-code generator to create this file from the resource file
using the command line:

```bash
> pyrcc5 FMIGenerator.qrc -o FMIGenerator_rc.py
```

To automate the process (which needs to be done whenever a ui file has been edited) the
script `update.sh` is available. Run this, whenever you have modified a ui file!

