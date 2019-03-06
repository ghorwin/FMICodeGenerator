#!/bin/bash

# -x     - generate test code to show and test the class
# -i 0   - generate class using tabs as indentation

pyuic5 -x -i 0 WizardPageBasicProperties.ui -o Ui_WizardPageBasicProperties.py
pyuic5 -x -i 0 WizardPageVariables.ui -o Ui_WizardPageVariables.py

