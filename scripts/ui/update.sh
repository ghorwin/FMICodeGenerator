#!/bin/bash

# -x     - (optional) generate test code to show and test the class
# -i 0   - generate class using tabs as indentation

pyuic5 -i 0 WizardPageBasicProperties.ui -o ../Ui_WizardPageBasicProperties.py
pyuic5 -i 0 WizardPageVariables.ui -o ../Ui_WizardPageVariables.py
pyuic5 -i 0 WizardPageGenerate.ui -o ../Ui_WizardPageGenerate.py


# also transform the qrc file

pyrcc5 FMIGenerator.qrc -o ../FMIGenerator_rc.py

