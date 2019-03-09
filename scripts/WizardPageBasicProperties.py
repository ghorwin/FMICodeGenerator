#!/usr/bin/python
# -*- coding: utf-8 -*-

# Implementation of the basic properties wizard page.
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
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QDir

from ui.Ui_WizardPageBasicProperties import Ui_WizardPageBasicProperties

from FMIGenerator import FMIGenerator


class WizardPageBasicProperties(QWidget):
	loadDefaults = pyqtSignal('QString')
	
	def __init__(self):
		super(WizardPageBasicProperties, self).__init__()
		self.ui = Ui_WizardPageBasicProperties()
		self.ui.setupUi(self)
		self.ui.lineEditTargetDir.setText( QDir.home().absolutePath() )
		self.show()
	
	@pyqtSlot()
	def on_lineEditModelName_editingFinished(self):
		# auto-generate filename for FMU unless previously entered/selected
		targetFileName = os.path.join(self.ui.lineEditTargetDir.text(), self.ui.lineEditModelName.text().strip())
		self.ui.lineEditFMUFilePath.setText(targetFileName)
		inputDataCacheFile = targetFileName + ".input"
		if (os.path.exists(inputDataCacheFile)):
			res = QMessageBox.question(self, "Import previous definitions", 
			                           "A file with input data for the same FMU exists. Re-load input data?")
			if res == QMessageBox.No:
				return
			fmiGenerator = FMIGenerator()
			fmiGenerator.readInputData(inputDataCacheFile)
			self.ui.plainTextEditDescription.setPlainText(fmiGenerator.description)
			self.loadDefaults.emit(inputDataCacheFile)
			


	@pyqtSlot()
	def on_lineEditTargetDir_editingFinished(self):
		self.on_lineEditModelName_editingFinished()


	@pyqtSlot()
	def on_toolButtonBrowseFilename_clicked(self):
		# open browse filename dialog
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		options |= QFileDialog.ShowDirsOnly
		options |= QFileDialog.DontResolveSymlinks
		
		targetDir = QFileDialog.getExistingDirectory(self, "Select/enter target directory for FMU", QDir.home().absolutePath(),
		                                                options=options)
		if targetDir:
			self.ui.lineEditTargetDir.setText(targetDir)
			self.on_lineEditModelName_editingFinished()
			return True
