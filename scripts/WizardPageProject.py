#!/usr/bin/env python3

# Implementation of the project selection wizard page (create new or open existing FMU project).
#
#
# This file is part of FMICodeGenerator (https://github.com/ghorwin/FMICodeGenerator)
#
# BSD 3-Clause License
#
# Copyright (c) 2018, Andreas Nicolai
# All rights reserved.
#
# see https://github.com/ghorwin/FMICodeGenerator/blob/master/LICENSE for details.

from PyQt6.QtWidgets import QWidget, QFileDialog
from PyQt6.QtCore import pyqtSlot, QDir

from Ui_WizardPageProject import Ui_WizardPageProject


class WizardPageProject(QWidget):
	def __init__(self):
		super().__init__()
		self.ui = Ui_WizardPageProject()
		self.ui.setupUi(self)
		self.updateEnabledState()
		self.show()


	def openExisting(self):
		return self.ui.radioButtonOpen.isChecked()


	def updateEnabledState(self):
		enabled = self.openExisting()
		self.ui.labelProjectDir.setEnabled(enabled)
		self.ui.lineEditProjectDir.setEnabled(enabled)
		self.ui.toolButtonBrowseProject.setEnabled(enabled)


	@pyqtSlot(bool)
	def on_radioButtonOpen_toggled(self, checked):
		self.updateEnabledState()


	@pyqtSlot()
	def on_toolButtonBrowseProject_clicked(self):
		options = (QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.ShowDirsOnly |
				   QFileDialog.Option.DontResolveSymlinks)

		startDir = self.ui.lineEditProjectDir.text().strip()
		if not startDir:
			startDir = QDir.home().absolutePath()
		projectDir = QFileDialog.getExistingDirectory(self, "Select existing FMU project directory", startDir,
													  options=options)
		if projectDir:
			self.ui.lineEditProjectDir.setText(projectDir)
