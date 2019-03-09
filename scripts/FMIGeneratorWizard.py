#!/usr/bin/python
# -*- coding: utf-8 -*-

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

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal 
from PyQt5 import QtCore, QtWidgets

from WizardPageBasicProperties import WizardPageBasicProperties
from WizardPageVariables import WizardPageVariables
from WizardPageGenerate import WizardPageGenerate
from FMIGenerator import FMIGenerator, VarDef


class FMIGeneratorWizard(QtWidgets.QWizard):
	def __init__(self, parent=None):
		super(FMIGeneratorWizard, self).__init__(parent)
		self.addPage(PageBasicProperties(self))
		self.addPage(PageVariables(self))
		generatePage = PageGenerate(self)
		generatePage.pageBasicProps = self.page(0).page # get WizardPageBasicProperties
		generatePage.pageVars = self.page(1).page # get WizardPageVariables
		self.addPage(generatePage)
		
		# connect the signal/slots between pages
		generatePage.pageBasicProps.loadDefaults.connect(generatePage.pageVars.onLoadDefaults)
		
		self.setWindowTitle("FMI Generator Wizard")
		self.resize(1400,600)


class PageBasicProperties(QtWidgets.QWizardPage):
	def __init__(self, parent=None):
		super(PageBasicProperties, self).__init__(parent)
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
		# check if directory exists and is a file
		if os.path.exists(fmuTargetDir):
			if os.path.isfile(fmuTargetDir):
				QtWidgets.QMessageBox.critical(self, "Invalid input", "There exists already a file at '{}'.".format(fmuTargetDir))
				self.page.ui.lineEditTargetDir.selectAll()
				self.page.ui.lineEditTargetDir.setFocus()
				return False
			res = QtWidgets.QMessageBox.question(self, "Invalid input", "Target directory exists. Overwrite?")
			if res == QtWidgets.QMessageBox.No:
				self.page.ui.lineEditTargetDir.selectAll()
				self.page.ui.lineEditTargetDir.setFocus()
				return False
		# input is ok, proceed to next page
		return True


class PageVariables(QtWidgets.QWizardPage):
	def __init__(self, parent=None):
		super(PageVariables, self).__init__(parent)
		layout = QtWidgets.QVBoxLayout()
		self.page = WizardPageVariables()
		layout.addWidget(self.page)
		self.setLayout(layout)
		self.setTitle("Variables and Parameters")

	def validatePage(self):
		# check all variables for valid combinations of parameters
		return True


class PageGenerate(QtWidgets.QWizardPage):
	def __init__(self, parent=None):
		super(PageGenerate, self).__init__(parent)
		layout = QtWidgets.QVBoxLayout()
		self.page = WizardPageGenerate()
		layout.addWidget(self.page)
		self.setLayout(layout)
		self.setTitle("Ready to generate FMU")

	def validatePage(self):
		# here we generate the actual FMU
		
		fmiGenerator = FMIGenerator()
		
		# basic properties
		fmiGenerator.modelName = self.pageBasicProps.ui.lineEditModelName.text().strip()
		fmiGenerator.description = self.pageBasicProps.ui.plainTextEditDescription.toPlainText()
		fmiGenerator.targetDir = self.pageBasicProps.ui.lineEditTargetDir.text()
		
		# variables
		fmiGenerator.variables = self.pageVars.variables

		fmiGenerator.autobuild = self.page.ui.checkBoxTestBuild.isChecked()
		
		try:
			fmiGenerator.generate()
			msgs = "\n".join(fmiGenerator.messages)
			self.page.ui.plainTextEditLog.setPlainText(msgs)
		except Exception as e:
			msgs = "\n".join(fmiGenerator.messages)
			self.page.ui.plainTextEditLog.setPlainText(msgs)
			QtWidgets.QMessageBox.critical(self, "FMI Generation Error", "Some error occurred during FMI generation:\n{}".format(e.message))
			return False
		
		QtWidgets.QMessageBox.information(self, "FMU Generation Completed", 
		                                  "FMU source code directory '{}' created successfully."
		                                  .format(self.pageBasicProps.ui.lineEditTargetDir.text()))
		return True

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	wizard = FMIGeneratorWizard()
	wizard.show()
	sys.exit(app.exec_())