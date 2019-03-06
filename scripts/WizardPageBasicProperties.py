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
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog

from ui.Ui_WizardPageBasicProperties import Ui_WizardPageBasicProperties

class WizardPageBasicProperties(QWidget):
	def __init__(self):
		super(WizardPageBasicProperties, self).__init__()
		self.ui = Ui_WizardPageBasicProperties()
		self.ui.setupUi(self)
		# must manually connect the tool button - connect by name causes duplicate call to slot
		self.ui.toolButtonBrowseFilename.clicked.connect(self.on_toolButtonBrowseFilename_clicked2)
		self.show()
		
	def on_lineEditModelName_editingFinished(self):
		# auto-generate filename for FMU unless previously entered/selected
		if self.ui.lineEditModelName.text().strip() and not self.ui.lineEditFilePath.text():
			self.ui.lineEditFilePath.setText( self.ui.lineEditModelName.text().strip() + ".fmu")

	def on_toolButtonBrowseFilename_clicked2(self):
		# open browse filename dialog
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self, "Select/enter target FMU name","","FMUs (*.fmu);;All files (*)", 
		                                          options=options)
		if fileName:
			# append .fmu extension unless already given
			if len(fileName) < 4 or fileName[:-4] != ".fmu":
				fileName = fileName + ".fmu"
			self.ui.lineEditFilePath.setText(fileName)
			return True
