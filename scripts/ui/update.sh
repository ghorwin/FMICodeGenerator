#!/bin/bash

# -x     - (optional) generate test code to show and test the class
# -i 0   - generate class using tabs as indentation

pyuic6 -i 0 WizardPageBasicProperties.ui -o ../Ui_WizardPageBasicProperties.py
pyuic6 -i 0 WizardPageVariables.ui -o ../Ui_WizardPageVariables.py
pyuic6 -i 0 WizardPageGenerate.ui -o ../Ui_WizardPageGenerate.py
pyuic6 -i 0 WizardPageProject.ui -o ../Ui_WizardPageProject.py

# Note: PyQt6 has no resource compiler anymore; the tool button icons are
# loaded at runtime from ui/gfx (see WizardPageVariables.py).
