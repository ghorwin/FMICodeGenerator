#!/usr/bin/env python3

# The Wizard, that collects all data needed to generate the FMU from the user.
#
#
# This file is part of FMICodeGenerator (https://github.com/ghorwin/FMICodeGenerator)
#
# BSD 3-Clause License
#
# Copyright (c) 2018, Andreas Nicolai
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import sys
import os.path

from PyQt6 import QtWidgets

from WizardPageProject import WizardPageProject, addRecentProject
from WizardPageBasicProperties import WizardPageBasicProperties
from WizardPageVariables import WizardPageVariables
from WizardPageGenerate import WizardPageGenerate
from FMIGenerator import FMIGenerator, VarDef, findProjectInputFile, startValueMissing, startValueUnneeded
from TooltipPopup import TooltipEventFilter

# page IDs
PAGE_PROJECT = 0
PAGE_BASIC_PROPERTIES = 1
PAGE_VARIABLES = 2
PAGE_GENERATE = 3

# wizard modes
MODE_NEW = "new"
MODE_UPDATE = "update"


class FMIGeneratorWizard(QtWidgets.QWizard):
	def __init__(self, parent=None):
		super().__init__(parent)

		# mode is set by project page: MODE_NEW or MODE_UPDATE
		self.mode = MODE_NEW
		# in update mode: absolute path to the existing project directory
		self.projectDir = ""

		self.setPage(PAGE_PROJECT, PageProject(self))
		self.setPage(PAGE_BASIC_PROPERTIES, PageBasicProperties(self))
		self.setPage(PAGE_VARIABLES, PageVariables(self))
		self.setPage(PAGE_GENERATE, PageGenerate(self))

		# debug helper code
		#self.page(PAGE_BASIC_PROPERTIES).page.ui.lineEditModelName.setText("P_Control")
		#self.page(PAGE_BASIC_PROPERTIES).page.ui.lineEditTargetDir.setText("/home/ghorwin/git/FMICodeGenerator/examples")
		#self.page(PAGE_BASIC_PROPERTIES).page.on_lineEditModelName_editingFinished()

		self.setWindowTitle("FMI Generator Wizard")
		self.resize(800,600)


	def basicPropsPage(self):
		return self.page(PAGE_BASIC_PROPERTIES).page


	def variablesPage(self):
		return self.page(PAGE_VARIABLES).page


class PageProject(QtWidgets.QWizardPage):
	def __init__(self, parent=None):
		super().__init__(parent)
		layout = QtWidgets.QVBoxLayout()
		self.page = WizardPageProject()
		layout.addWidget(self.page)
		self.setLayout(layout)
		self.setTitle("FMU project")
		self.page.recentProjectActivated.connect(lambda: self.wizard().next())


	def nextId(self):
		# when opening an existing project, model name and location are fixed: skip basic properties page
		if self.page.openExisting():
			return PAGE_VARIABLES
		return PAGE_BASIC_PROPERTIES


	def validatePage(self):
		wizard = self.wizard()
		if not self.page.openExisting():
			wizard.mode = MODE_NEW
			wizard.projectDir = ""
			return True

		projectDir = self.page.ui.lineEditProjectDir.text().strip()
		if len(projectDir) == 0 or not os.path.isdir(projectDir):
			QtWidgets.QMessageBox.critical(self, "Invalid input", "Please select an existing FMU project directory.")
			self.page.ui.lineEditProjectDir.setFocus()
			return False
		projectDir = os.path.abspath(projectDir)

		inputFile = findProjectInputFile(projectDir)
		if inputFile is None:
			QtWidgets.QMessageBox.critical(self, "Invalid project directory",
										   "The directory '{}' does not contain a (unique) FMU project file '<model name>.input'."
										   .format(projectDir))
			return False

		fmiGenerator = FMIGenerator()
		try:
			fmiGenerator.readInputData(inputFile)
		except Exception as e:
			QtWidgets.QMessageBox.critical(self, "Error reading project file",
										   "Cannot read project file '{}':\n{}".format(inputFile, e))
			return False
		if not fmiGenerator.modelName:
			fmiGenerator.modelName = os.path.basename(projectDir)

		if not os.path.isfile(os.path.join(projectDir, "src", fmiGenerator.modelName + ".cpp")):
			QtWidgets.QMessageBox.critical(self, "Invalid project directory",
										   "The directory '{}' does not contain the source file 'src/{}.cpp'."
										   .format(projectDir, fmiGenerator.modelName))
			return False

		if os.path.dirname(inputFile) != projectDir:
			QtWidgets.QMessageBox.information(self, "Old project format",
											  "The project file was found outside the project directory ('{}'). "
											  "When updating, the project file will be written into the project directory."
											  .format(inputFile))

		wizard.mode = MODE_UPDATE
		wizard.projectDir = projectDir

		# populate basic properties (used during generation) and variables
		basicProps = wizard.basicPropsPage()
		basicProps.ui.lineEditModelName.setText(fmiGenerator.modelName)
		basicProps.ui.lineEditTargetDir.setText(os.path.dirname(projectDir))
		basicProps.ui.lineEditFMUFilePath.setText(projectDir)
		basicProps.ui.plainTextEditDescription.setPlainText(fmiGenerator.description)
		wizard.variablesPage().onLoadDefaults(inputFile)
		return True


class PageBasicProperties(QtWidgets.QWizardPage):
	def __init__(self, parent=None):
		super().__init__(parent)
		layout = QtWidgets.QVBoxLayout()
		self.page = WizardPageBasicProperties()
		layout.addWidget(self.page)
		self.setLayout(layout)
		self.setTitle("Basic properties of the Functional Mock-up Unit")


	def validatePage(self):
		# check for mandatory input
		fmuName = self.page.ui.lineEditModelName.text().strip()
		if len(fmuName) == 0:
			QtWidgets.QMessageBox.critical(self, "Missing input", "A model name is required.")
			self.page.ui.lineEditModelName.selectAll()
			self.page.ui.lineEditModelName.setFocus()
			return False
		fmuTargetDir = self.page.ui.lineEditTargetDir.text().strip() # this is the base directory where the target directory is created
		if len(fmuTargetDir) == 0:
			QtWidgets.QMessageBox.critical(self, "Missing input", "A target directory is required.")
			self.page.ui.lineEditTargetDir.selectAll()
			self.page.ui.lineEditTargetDir.setFocus()
			return False
		# compose directory including subdir
		fmuTargetDir = os.path.join(fmuTargetDir, fmuName)
		# refuse to overwrite an existing directory/file - existing projects must be opened instead
		if os.path.exists(fmuTargetDir):
			if os.path.isfile(fmuTargetDir):
				msg = "There exists already a file at '{}'.".format(fmuTargetDir)
			else:
				msg = ("The directory '{}' exists already. To update an existing FMU project, go back and "
					   "select 'Open an existing FMU project'.".format(fmuTargetDir))
			QtWidgets.QMessageBox.critical(self, "Invalid input", msg)
			self.page.ui.lineEditModelName.selectAll()
			self.page.ui.lineEditModelName.setFocus()
			return False
		# input is ok, proceed to next page
		return True


class PageVariables(QtWidgets.QWizardPage):
	def __init__(self, parent=None):
		super().__init__(parent)
		layout = QtWidgets.QVBoxLayout()
		self.page = WizardPageVariables()
		layout.addWidget(self.page)
		self.setLayout(layout)
		self.setTitle("Variables and Parameters")

	def validatePage(self):
		# check all variables for valid combinations of parameters
		# variables must not start with a number and must not container non-Ascii chars

		capitalized_var_names = set()

		for i in range(len(self.page.variables)):
			varname = self.page.variables[i].name

			# check if the leading character is a number
			if len(varname) == 0:
				QtWidgets.QMessageBox.critical(self, "Invalid variable name", "Please specify names for all variables!")
				return False
			if varname[0] >= '0' and varname[0] <= '9':
				QtWidgets.QMessageBox.critical(self, "Invalid variable name", "Variables must not begin with a number.")
				return False
			for a in varname:
				if a in ' \t.*-/\\!"':
					QtWidgets.QMessageBox.critical(self, "Invalid variable name", "Variables must not contain spaces or tab characters or other special characters.")
					return False
				lowerCaseChar = (ord(a) >= ord('a') and ord(a) <= ord('z'))
				upperCaseChar = (ord(a) >= ord('A') and ord(a) <= ord('Z'))
				isNumber = (ord(a) >= ord('0') and ord(a) <= ord('9'))
				if not isNumber and not lowerCaseChar and not upperCaseChar and a!='_':
					QtWidgets.QMessageBox.critical(self, "Invalid variable name", "Variable names must only use ASCII characters (a-z, A-Z) and or numbers or '_' characters.")
					return False
			capVarName = varname.upper()
			if capVarName in capitalized_var_names:
				QtWidgets.QMessageBox.critical(self, "Invalid variable name", "Variable names must be unique (case in-sensitive).")
				return False
			capitalized_var_names.add(capVarName)

		# required start values must be given
		missing = [v.name for v in self.page.variables if startValueMissing(v)]
		if len(missing) != 0:
			QtWidgets.QMessageBox.critical(self, "Missing start value",
				"The following variables require a start value: {}".format(", ".join(missing)))
			self.selectVariable(missing[0])
			return False

		# start values that are not needed are only written on request
		unneeded = [v.name for v in self.page.variables if startValueUnneeded(v)]
		self.page.writeUnneededStartValues = False
		if len(unneeded) != 0:
			msgBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, "Unneeded start values",
				"The following variables have a start value, which is not needed and hence ignored by the "
				"master: {}\n\nShall these start values still be written to modelDescription.xml?"
				.format(", ".join(unneeded)), parent=self)
			btnYes = msgBox.addButton("Yes", QtWidgets.QMessageBox.ButtonRole.YesRole)
			msgBox.addButton("No", QtWidgets.QMessageBox.ButtonRole.NoRole)
			btnBack = msgBox.addButton("Back", QtWidgets.QMessageBox.ButtonRole.RejectRole)
			msgBox.setDefaultButton(btnBack)
			msgBox.setEscapeButton(btnBack)
			msgBox.exec()
			if msgBox.clickedButton() is btnBack:
				self.selectVariable(unneeded[0])
				return False
			self.page.writeUnneededStartValues = msgBox.clickedButton() is btnYes

		return True


	def selectVariable(self, name):
		"""Selects the variable with the given name and focuses the start value field."""
		for i, var in enumerate(self.page.variables):
			if var.name == name:
				self.page.ui.tableWidget.selectRow(i)
				self.page.ui.lineEditStart.setFocus()
				return


class PageGenerate(QtWidgets.QWizardPage):
	def __init__(self, parent=None):
		super().__init__(parent)
		layout = QtWidgets.QVBoxLayout()
		self.page = WizardPageGenerate()
		layout.addWidget(self.page)
		self.setLayout(layout)


	def initializePage(self):
		wizard = self.wizard()
		self.page.ui.plainTextEditLog.clear()
		if wizard.mode == MODE_UPDATE:
			self.setTitle("Ready to update FMU project")
			self.setSubTitle("Only generated files are overwritten in '{}'. Your source code is not modified.".format(wizard.projectDir))
			self.setButtonText(QtWidgets.QWizard.WizardButton.FinishButton, "Update FMU")
		else:
			self.setTitle("Ready to generate FMU")
			self.setSubTitle("")
			self.setButtonText(QtWidgets.QWizard.WizardButton.FinishButton, "Generate FMU")


	def validatePage(self):
		# here we generate/update the actual FMU
		wizard = self.wizard()
		basicProps = wizard.basicPropsPage()

		fmiGenerator = FMIGenerator()

		# basic properties
		fmiGenerator.modelName = basicProps.ui.lineEditModelName.text().strip()
		fmiGenerator.description = basicProps.ui.plainTextEditDescription.toPlainText()
		fmiGenerator.targetDir = basicProps.ui.lineEditTargetDir.text()

		# variables
		fmiGenerator.variables = wizard.variablesPage().variables
		fmiGenerator.writeUnneededStartValues = wizard.variablesPage().writeUnneededStartValues

		fmiGenerator.autobuild = self.page.ui.checkBoxTestBuild.isChecked()

		try:
			if wizard.mode == MODE_UPDATE:
				fmiGenerator.update(wizard.projectDir)
			else:
				fmiGenerator.generate()
			msgs = "\n".join(fmiGenerator.messages)
			self.page.ui.plainTextEditLog.setPlainText(msgs)
		except Exception as e:
			msgs = "\n".join(fmiGenerator.messages)
			self.page.ui.plainTextEditLog.setPlainText(msgs)
			QtWidgets.QMessageBox.critical(self, "FMI Generation Error", "Some error occurred during FMI generation:\n{}".format(str(e)))
			return False

		# remember project directory in list of recently generated FMU projects
		addRecentProject(fmiGenerator.targetDirPath)

		if wizard.mode == MODE_UPDATE:
			QtWidgets.QMessageBox.information(self, "FMU Update Completed",
											  "FMU project '{}' updated. Please check the generation log for details."
											  .format(fmiGenerator.targetDirPath))
		else:
			QtWidgets.QMessageBox.information(self, "FMU Generation Completed",
											  "FMU source code directory '{}' created successfully."
											  .format(fmiGenerator.targetDirPath))
		return True

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	# show widget tooltips in the custom tooltip card
	app.installEventFilter(TooltipEventFilter(app))
	wizard = FMIGeneratorWizard()
	wizard.show()
	sys.exit(app.exec())
